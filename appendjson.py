import json

# Open the text file and read the lines
with open("text_file.txt", "r") as f:
    items = f.readlines()

# Create an empty list to store the data
data = []

# Loop through each line and add the data to the list
for item in items:
    filename, sha256 = item.strip().split("\t")
    data.append({"filename": filename, "sha256": sha256})

# Open the JSON file and load the existing data
with open("db.json", "r") as f:
    existing_data = json.load(f)

# Merge the existing data with the new data
existing_data += data

# Write the updated data back to the JSON file
with open("data.json", "w") as f:
    json.dump(existing_data, f)
