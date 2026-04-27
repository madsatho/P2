import json
import os

directory = "Works_ids_json"
all_short_ids = []

for filename in os.listdir(directory):
    if filename.endswith(".json") and filename.startswith("works_ids_page_"):

        filepath = os.path.join(directory, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

            for work in data:
                full_id = work["id"]
                short_id = full_id.split("/")[-1]
                all_short_ids.append(short_id)

with open("all_short_ids.txt", "w", encoding="utf-8") as f:
    for sid in all_short_ids:
        f.write(sid + "\n")