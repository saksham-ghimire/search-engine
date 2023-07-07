import string
from gensim.parsing.preprocessing import remove_stopwords
from django.http import JsonResponse
from django.shortcuts import render
from classifier import CLASSIFIER, VECTORIZER
from main.cron import get_df

def index(request):
    return render(request, template_name='index.html')

def classifier(request):
    if request.method == "POST":
        text = request.POST.get("query")
        if text:
            return JsonResponse(
                {"class" : classify_text(text)}
            )
    return render(request, template_name='classifier.html')


def process_text(text):
    filtered_text = remove_stopwords(text)
    filtered_text = filtered_text.translate(str.maketrans("", "", string.punctuation))
    normalized_text = filtered_text.lower()
    return normalized_text


def get_documents_id_in_order_of_relevancy(all_relevant_documents):
    if all_relevant_documents:
        high_priority = set.intersection(*(map(set, all_relevant_documents)))
        matching_documets = list({i for each in all_relevant_documents for i in each})

        def sort_prioriry(x):
            if x in high_priority:
                return 0, x
            return 1, x

        matching_documets.sort(key=sort_prioriry)
        return matching_documets
    return []


def get_inverted_index(dataframe):
    inverted_index = {}
    for index, row in dataframe.iterrows():
        title = row['title']
        keywords = title.split()

        for keyword in keywords:
            if keyword not in inverted_index:
                inverted_index[keyword] = [index]
            else:
                inverted_index[keyword].append(index)
    return inverted_index

def classify_text(text):
    # Transform the testing data into numerical features
    test_features = VECTORIZER.transform([text])

    # Make predictions on the testing data
    predictions = CLASSIFIER.predict(test_features)

    return list(predictions)


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        query = process_text(query)
        df = get_df()
        df.title = df.title.apply(process_text)
        df.author = df.author.apply(process_text)
        inverted_index = get_inverted_index(df)
        related_documents = []

        for each_word in query.split():
            if documents := inverted_index.get(each_word):
                related_documents.append(documents)

        relevant_documents = get_documents_id_in_order_of_relevancy(related_documents)
        selected_rows = df.iloc[[df.index.get_loc(index) for index in relevant_documents]]
        selected_rows.insert(0, 'SN', range(1, len(selected_rows) + 1))
        data = selected_rows.to_dict(orient='records')

        return JsonResponse({'data': data})
