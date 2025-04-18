import anthropic
import json

client = anthropic.Anthropic()

websites = []
website_categories = {}

# A .txt file containing a list of websites in the format "www.example.com", one per line
in_filename = "websites.txt"

# A .txt file to store the website categories in the format "www.example.com, <category>", one per line
out_filename = "website_categories.txt"

websites_with_categories = []
with open(out_filename, "r") as out_file:
    for line in out_file:
        line = line.strip()
        website, _ = line.split(", ", maxsplit=1)
        websites_with_categories.append(website)

with open(in_filename, "r") as in_file:
    for line in in_file:
        line = line.strip()
        websites.append(line)

for website in websites:
    if website not in websites_with_categories:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"What is the industry categorization of the website \"{website}\"? Present the answer in JSON format with a single key \"category\" and the value as the industry category of the website."},
                {"role": "assistant", "content": "{"}
            ]
        )
        response_text = "{" + response.content[0].text
        try:
            category = json.loads(response_text)["category"]
        except json.JSONDecodeError:
            print(f"Failed to decode JSON for website: {website}")
            category = "Unknown"
        website_categories[website] = category
        with open(out_filename, "a") as out_file:
            out_file.write(f"{website}, {category}\n")
