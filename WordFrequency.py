
import csv
from nltk.probability import FreqDist
import matplotlib.pyplot as plt
from collections import Counter
import re
from matplotlib.font_manager import FontProperties

# Set Bengali font
bengali_font = FontProperties(fname="Li Alinur Tatsama Unicode.ttf")


csv_file_path = 'Tokenized/RobTheKing.csv'
word_freq_dist = FreqDist()
text = []


def remove_punctuations(sentence):
    punctuations = '।,;:?!\'."-[]{}()–—―~'
    clean_sentence = re.sub(f"[{re.escape(punctuations)}]", '', sentence)
    return clean_sentence


# Open the CSV file
with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)

    # Iterate through each row
    for row in csv_reader:
        tokenized_sentence = row['tokenized_sentence']
        tokenized_sentence = remove_punctuations(tokenized_sentence)
        text.append(tokenized_sentence)

all_text = " ".join(text)
words = all_text.split()
word_freq = Counter(words)
num_common_words = 20
common_words = word_freq.most_common(num_common_words)
word_labels, word_counts = zip(*common_words)

print(word_labels)
plt.figure(figsize=(12, 6))
plt.bar(word_labels, word_counts, color='purple')
plt.xlabel('Words', fontproperties=bengali_font)  # Set Bengali font for xlabel
plt.ylabel('Frequency', fontproperties=bengali_font)  # Set Bengali font for ylabel
plt.title('Most Common Words in Dataset', fontproperties=bengali_font)  # Set Bengali font for title
plt.xticks( fontsize=8, fontproperties=bengali_font)  # Set Bengali font for xtick labels
plt.tight_layout()
plt.show()

