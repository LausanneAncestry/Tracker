import json

# Load the JSON from a file
with open("analysis\\results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort each year's dictionary by value descending
sorted_data = {
    year: dict(sorted(occupations.items(), key=lambda item: item[1], reverse=True))
    for year, occupations in data.items()
}

# Save the sorted JSON to a new file
with open("analysis\\results.json", "w", encoding="utf-8") as f:
    json.dump(sorted_data, f, indent=4, ensure_ascii=False)

print("Sorting complete. Saved to sorted_output.json.")
