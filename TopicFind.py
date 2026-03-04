import pyalex
available_papers={}
pyalex.config.api_key = "V11Jtt2BpqUgS9jg50bbnu"

print(pyalex.Works().count())
print(pyalex.Works().filter(primary_topic={"id": "https://openalex.org/T10102"}).count())


next_cursor = "*"

while next_cursor:
    # fetch one page
    topics_page = pyalex.Topics().get(cursor=next_cursor, per_page=200)

    for topic in topics_page:
        works_count = topic.get("works_count", 0)
        if 1000 <= works_count <= 5000:
            available_papers.update({topic['display_name']: works_count})

    # get next cursor from the .meta property
    next_cursor = topics_page.meta.get("next_cursor")

for a, b in available_papers.items():
    print(f"{a}: {b}")