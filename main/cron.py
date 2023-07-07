from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd


def get_df():
    df = pd.read_csv("data.csv")
    return df


def get_members_of_centre_for_intelligent_healthcare():
    response = requests.get(
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-intelligent-healthcare/persons/")
    relevant_authors = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        div_element = soup.find_all("div", class_="rendering rendering_person rendering_short rendering_person_short")

        for element in div_element:
            person, department = "", ""
            if exists := element.find("a", "link person"):
                person = exists.find("span").text
            relevant_authors.append(person)
    else:
        print(f"Error: {response.status_code}")

    return relevant_authors


def slugify(author):
    author = author.lower()
    return '-'.join(author.split())


def update_crawled_data():
    print(f'Starting crawl to fetch for updates in data')

    authors = get_members_of_centre_for_intelligent_healthcare()

    file = open("data.csv", "w")
    writer = csv.writer(file)
    writer.writerow(["title", "author", "year", "link"])
    for each_author in authors:
        slugified_author = slugify(each_author)
        publications_url = f'https://pureportal.coventry.ac.uk/en/persons/{slugified_author}/publications'
        response = requests.get(publications_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            result_divs = soup.find_all("div", class_="result-container")
            for div in result_divs:
                title_element = div.find("h3", class_="title")
                if title_element:
                    title = title_element.get_text(strip=True)
                    link = title_element.find("a")['href']
                    search_result_group = div.find_previous_sibling("div", class_="search-result-group")
                    if search_result_group:
                        year = search_result_group.get_text(strip=True)
                    writer.writerow([title, each_author, year, link])

    file.close()

