import pandas as pd
import math
import requests

class Topics:
    def finde_topics(self):
        url = "https://api.openalex.org/topics"

        params = {
            "sort": "works_count:desc",
            "per-page": 25,
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

        return records

    def topics_count(self, topic_id: str):
        per_page = 200

        url = "https://api.openalex.org/works"

        params = {
            "filter": f"topics.id:{topic_id}",
            "per-page": per_page,
            "page": 1
        }

        r = requests.get(url, params=params)
        data = r.json()

        total_results = data["meta"]["count"]
        total_pages = math.ceil(total_results / per_page)

        records = {
            "Total results:" : total_results,
            "Total pages:" : total_pages
        }

        return records

    def any_lise_topics(self):
        topics = self.finde_topics()
        rows = []

        for topic in topics:
            record = self.topics_count(topic["id"])
            rows.append(
                {
                    "id": topic["id"].rsplit("/", 1)[-1],
                    "title": topic["title"],
                    "total_results": record["Total results:"],
                    "total_pages": record["Total pages:"],
                    "pages": 0
                }
            )

        df = pd.DataFrame(rows)
        df.to_csv("MetaData.csv", index=False)

tp = Topics()
tp.anylise_topics()
