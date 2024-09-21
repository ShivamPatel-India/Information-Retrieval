import csv
import math

# Reading the documents from a CSV file
documents = []
with open('collection.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row
    for row in reader:
        documents.append(row[0])  # Document text in the first column

# Conducting stopword removal for pronouns/conjunctions
# for simplicity, only the stop words that are occurring in the given documents are included here
stopWords = {"i", "and", "she", "her", "they", "their",}


def perform_stopwords_removal(doc):
    words = doc.lower().split()
    return [word for word in words if word not in stopWords]

# Conducting stemming
stemming = {
    "cats": "cat",
    "dogs": "dog",
    "loves": "love",
    "love": "love"
}


def perform_stemming(words):
    return [stemming.get(word, word) for word in words]

# Preprocessing the documents (removing stopwords and applying stemming)
cleaned_documents = []
for doc in documents:
    words = perform_stopwords_removal(doc)
    stemmed_words = perform_stemming(words)
    cleaned_documents.append(stemmed_words)


# Identifying the index terms (vocabulary)
terms = ['love', 'cat', 'dog']  # Fixed order of terms for TF-IDF calculation

# Calculating TF (Term Frequency), IDF (Inverse Document Frequency), and TF-IDF
N = len(cleaned_documents)

# Function to calculate term frequency (TF)
def calculate_tf(term, doc):
    return doc.count(term) / len(doc)  # Normalized term frequency

# Function to calculate inverse document frequency (IDF)
def calculate_idf(term):
    doc_count = sum(1 for doc in cleaned_documents if term in doc)
    return math.log10(N / doc_count) if doc_count > 0 else 0


# Constructing the TF-IDF document-term matrix
docTermMatrix = []
for doc in cleaned_documents:
    tfidf_values = []
    for term in terms:
        tf = calculate_tf(term, doc)
        idf = calculate_idf(term)
        tf_idf = tf * idf
        tfidf_values.append(tf_idf)
    docTermMatrix.append(tfidf_values)

# Printing the document-term matrix
print("\nDocument-Term Matrix:")
print(f"{'':<15}{'love':<10}{'cat':<10}{'dog':<10}")  # Terms
for idx, doc_label in enumerate(['d1', 'd2', 'd3']):
    row = [f"{doc_label:<15}"] + \
        [f"{value:.2f}".ljust(10) for value in docTermMatrix[idx]]
    print("".join(row))
