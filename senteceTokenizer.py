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
csv_file_path = "PreTokenized Dataset/Humayun-Ahmed-Dataset_Toishi_Thesis-Sheet1.csv"
with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        author = row['author']
        content = row['content']

        # Tokenize sentences
        sentences = tokenizer.sentence_tokenizer(content)

        # Append tokenized sentences and novel name to the list
        for sentence in sentences:

            if sentence[0] == "”" or sentence[0] == "“" or sentence[0] == "‘" or sentence[0] == "’":
                continue
            else:
                if "“" in sentence:
                    sentence+="”"
                    tokenized_sentences.append((author, sentence))
                else:
                    tokenized_sentences.append((author, sentence))

# Write tokenized sentences to a new CSV file
new_csv_file_path = "Tokenized/HumayunTheKing.csv"
with open(new_csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['author', 'tokenized_sentence']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for author, sentence in tokenized_sentences:
        writer.writerow({'author': author, 'tokenized_sentence': sentence})

print("Tokenized sentences saved to:", new_csv_file_path)



