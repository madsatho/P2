import requests
import json
import os

url = "https://api.openalex.org/works"
folder = "Works_ids_json"
os.makedirs(folder, exist_ok=True)

cursor = "*"  # initial cursor
page = 1

while True:
    file_path = os.path.join(folder, f"works_ids_page_{page}.json")

    # Skip page if already saved
    if os.path.exists(file_path):
        print(f"Page {page} already exists. Skipping...")
        page += 1
        continue

    params = {
        "filter": "topics.id:T14423",
        "per-page": 200,
        "cursor": cursor,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        print(f"Request failed: {e}. Retrying...")
        continue

    if "results" not in data:
        print("API error:", data)
        break

    records = []
    for work in data["results"]:
        records.append({
            "id": work.get("id"),
            "title": work.get("display_name"),
            "authors": [
                {"name": a["author"]["display_name"], "id": a["author"]["id"]}
                for a in work.get("authorships", [])
            ],
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Saved page {page} ({len(records)} records)")

    cursor = data["meta"].get("next_cursor")
    if not cursor:
        print("No more pages left.")
        break

    page += 1