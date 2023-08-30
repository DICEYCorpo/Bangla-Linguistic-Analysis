import csv
import sys
from bltk.langtools import Tokenizer
maxInt = sys.maxsize

# Increase the field size limit
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

# Create a tokenizer instance
tokenizer = Tokenizer()

# Initialize a list to store tokenized sentences and novel names
tokenized_sentences = []

# Read the CSV file
csv_file_path = "Tokenized/sharatchandra.csv"
with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        content = row['Text']

        author = row['Author']
        if content[0] == "”" or content[0] == "“" or content[0] == "‘" or content[0] == "’":
            continue
        else:
            if "“" in content:
                content+="”"
                tokenized_sentences.append((author, content))
            else:
                tokenized_sentences.append((author, content))

# Write tokenized sentences to a new CSV file
new_csv_file_path = "Tokenized/RobTheKing.csv"
with open(new_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['novel_name', 'tokenized_sentence']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for novel_name, sentence in tokenized_sentences:
        writer.writerow({'novel_name': novel_name, 'tokenized_sentence': sentence})

print("Tokenized sentences saved to:", new_csv_file_path)



