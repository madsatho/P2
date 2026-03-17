import requests
import math
def finde_topics():
    url = "https://api.openalex.org/topics"
    params = {
        "sort": "works_count:desc",
        "per-page": 100,  # correct parameter name
        "page": 1
    }

    r = requests.get(url, params=params)
    topics = r.json()

    records = []

    for topic in topics["results"]:
        records.append({
            "id": topic.get("id"),
            "title": topic.get("display_name")
        })

        print("ID:", topic.get("id"))
        print("Title:", topic.get("display_name"))

def topics_count(topic_id:str):
    per_page = 200

    url = "https://api.openalex.org/works"
    params = {
        "filter": f"topics.id:{topic_id}",
        "per-page": per_page,
        "page": 1
    }

    r = requests.get(url, params=params)
    data = r.json()

    total_results = data["meta"]["count"]  # total works in this topic
    total_pages = math.ceil(total_results / per_page)

    print("Total results:", total_results)
    print("Total pages:", total_pages)

finde_topics()
topics_count("T14423")