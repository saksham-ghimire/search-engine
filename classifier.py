from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from gensim.parsing.preprocessing import remove_stopwords
import string
import os

def process_text(text):
    filtered_text = remove_stopwords(text)
    filtered_text = filtered_text.translate(str.maketrans("", "", string.punctuation))
    normalized_text = filtered_text.lower()
    return normalized_text


def prepare_test_data():
    data_folder = 'data'  # Path to the main data folder
    folders = ['business', 'sports', 'health']  # List of folder names

    train_data = []  # List to store the tuples

    for folder in folders:
        folder_path = os.path.join(data_folder, folder)  # Path to the current folder
        files = os.listdir(folder_path)  # List of files inside the folder

        for file in files:
            file_path = os.path.join(folder_path, file)  # Path to the current file

            with open(file_path, 'r') as f:
                content = f.read()  # Read the content of the file
                train_data.append((process_text(content), folder))  # Append a tuple to the data list
    return train_data


def prepare_classifer_and_vectorizer():
    # Separate the features (text) and labels (classes)
    train_X = [data[0] for data in prepare_test_data()]
    train_y = [data[1] for data in prepare_test_data()]

    # Create a CountVectorizer to convert text to numerical features
    vectorizer = CountVectorizer()
    train_features = vectorizer.fit_transform(train_X)

    # Train the Naive Bayes classifier
    classifier = MultinomialNB()
    classifier.fit(train_features, train_y)
    return classifier, vectorizer


CLASSIFIER, VECTORIZER = prepare_classifer_and_vectorizer()

