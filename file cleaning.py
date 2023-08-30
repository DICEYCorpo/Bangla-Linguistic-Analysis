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

# Initialize a list to store tokenized sentences and novel names
tokenized_sentences = []

# Read the CSV file
csv_file_path = "Tokenized/Begum-Rokeya_Toishi-Sheet1Tokenized.csv"
punctuations = '।,;:?!\'."-[]{}()–—―~'
number = '১২৩৪৫৬৭৮৯'
with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        novel_name = row['novel_name']
        content = row['tokenized_sentence']
    # Append tokenized sentences and novel name to the list
        if content[0] in ["”", "“", "‘", "’", "'", ":", "”", "“", "‘", "’", "'", ":", "ঃ", '"',"*","-","—"]:
            content = content[1:].lstrip()
        if content[0] in punctuations:
            continue
        if content[0] in number+"।":
            continue

        else:
            if "“" in content:
                content+="”"
                tokenized_sentences.append((novel_name, content))
            else:
                tokenized_sentences.append((novel_name, content))

# Write tokenized sentences to a new CSV file
new_csv_file_path = "Tokenized/BegumTheQueen.csv"
with open(new_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['novel_name', 'tokenized_sentence']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for novel_name, sentence in tokenized_sentences:
        writer.writerow({'novel_name': novel_name, 'tokenized_sentence': sentence})

print("Cleaned sentences saved to:", new_csv_file_path)