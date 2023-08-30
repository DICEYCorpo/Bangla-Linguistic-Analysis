import csv
import re
from nltk import FreqDist
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

csv_file_path = 'Tokenized/RobTheKing.csv'


def remove_punctuations(sentence):
    punctuations = '।,;:?!\'."-[]{}()–—―~'
    clean_sentence = re.sub(f"[{re.escape(punctuations)}]", '', sentence)
    return clean_sentence


total_length = 0
sentence_count = 0

long_sentences = []  # Store sentences above average length
short_sentences = []  # Store sentences below average length

# Open the CSV file
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)

    # Iterate through each row
    for row in csv_reader:
        tokenized_sentence = row['tokenized_sentence']
        cleaned_sentence = remove_punctuations(tokenized_sentence)
        sentence_length = len(cleaned_sentence.split())  # Calculate length of cleaned sentence in words
        total_length += sentence_length
        sentence_count += 1

# Calculate average sentence length
if sentence_count > 0:
    average_length = total_length / sentence_count
    print(f"Average sentence length: {average_length:.2f} words")

    # Categorize sentences as long or short and perform analysis
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)

        for row in csv_reader:
            tokenized_sentence = row['tokenized_sentence']
            cleaned_sentence = tokenized_sentence
            sentence_length = len(cleaned_sentence.split())  # Calculate length of cleaned sentence in words

            if sentence_length > average_length:
                long_sentences.append(cleaned_sentence)
            else:
                short_sentences.append(cleaned_sentence)

    # Perform analysis on long and short sentences
    long_lengths = [len(sentence.split()) for sentence in long_sentences]
    short_lengths = [len(sentence.split()) for sentence in short_sentences]

    # Plot bar graphs
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(long_lengths, bins=20, color='blue', alpha=0.7)
    plt.title('Long Sentences')
    plt.xlabel('Sentence Length')
    plt.ylabel('Frequency')
    plt.gca().xaxis.set_major_locator(MultipleLocator(10))

    plt.subplot(1, 2, 2)
    plt.hist(short_lengths, bins=20, color='orange', alpha=0.7)
    plt.title('Short Sentences')
    plt.xlabel('Sentence Length')
    plt.ylabel('Frequency')
    plt.gca().xaxis.set_major_locator(MultipleLocator(1))

    plt.tight_layout()
    plt.show()

else:
    print("No sentences found in the CSV.")
