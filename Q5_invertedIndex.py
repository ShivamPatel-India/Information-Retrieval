from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self):
        # Initialize MongoDB connection and collections
        db = self.connect_to_mongodb()
        self.terms_collection = db['terms']  # Inverted index collection
        self.documents_collection = db['documents']  # Documents collection
        self.term_id_counter = 0  # Counter for term IDs
        self.document_id_counter = 0  # Counter for document IDs

        # Clear collections to avoid duplicates on restart
        self.terms_collection.delete_many({})
        self.documents_collection.delete_many({})

        # Private variables for TF-IDF vectorization and document vectors
        self.vectorizer = None  # TF-IDF vectorizer
        self.document_vectors = []  # TF-IDF vectors for documents
        self.terms_vocabulary = {}  # Vocabulary from TF-IDF vectorizer

    def connect_to_mongodb(self):
        """
        Establishes a connection to the MongoDB database.
        """
        DB_NAME = "CPP_Assignment4"  # Database name
        DB_HOST = "localhost"  # Hostname
        DB_PORT = 27017  # Port number
        try:
            client = MongoClient(host=DB_HOST, port=DB_PORT)
            db = client[DB_NAME]
            return db
        except:
            print("Database connection failed.")

    def add_document(self, document_content):
        """
        Adds a document to the MongoDB collection with a unique ID.
        """
        self.documents_collection.insert_one(
            {"_id": self.document_id_counter, "content": document_content}
        )
        self.document_id_counter += 1

    def add_term(self, position, documents):
        """
        Adds a term to the inverted index with its position and document references.
        """
        # Cast position to Python int
        position = int(position)
        # Cast document keys and values to native Python types
        documents = {str(k): float(v) for k, v in documents.items()}

        self.terms_collection.insert_one(
            {"_id": self.term_id_counter, "pos": position, "docs": documents}
        )
        self.term_id_counter += 1


    def generate_inverted_index(self):
        """
        Creates an inverted index using TF-IDF vectorization.
        """
        # Retrieve all documents from the MongoDB collection
        documents = [doc['content'] for doc in self.documents_collection.find()]

        # Generate TF-IDF vectors for documents using n-grams (unigrams, bigrams, trigrams)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3))
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # Store the vocabulary and document vectors
        self.terms_vocabulary = self.vectorizer.vocabulary_
        self.document_vectors = tfidf_matrix.toarray()

        # Create an inverted index mapping terms to documents
        inverted_index = {}
        for document_id, term_id in zip(*tfidf_matrix.nonzero()):
            tfidf_value = tfidf_matrix[document_id, term_id]
            if term_id not in inverted_index:
                inverted_index[term_id] = {}
            inverted_index[term_id][str(document_id)] = float(tfidf_value)  # Cast to float

        # Insert the inverted index into the MongoDB collection
        for position, document_references in inverted_index.items():
            self.add_term(int(position), document_references)  # Ensure Python int


    def rank_documents(self, query):
        """
        Ranks documents based on their relevance to the given query using cosine similarity.
        """
        # Transform the query using the existing vocabulary and TF-IDF weights
        query_vector = self.vectorizer.transform([query]).toarray()[0]

        # Calculate cosine similarity for each document
        document_scores = []
        for document_id in range(self.document_id_counter):
            similarity_score = round(
                cosine_similarity([query_vector, self.document_vectors[document_id]])[0][1], 2
            )
            document_scores.append((document_id, similarity_score))

        # Sort documents by similarity score in descending order
        document_scores.sort(key=lambda x: x[1], reverse=True)

        # Display the ranked documents with non-zero similarity
        for document_id, similarity_score in document_scores:
            if similarity_score > 0:
                document = self.documents_collection.find_one({"_id": document_id})
                print(f"\"{document['content']}\", {similarity_score}")

if __name__ == '__main__':
    # Initialize the search engine
    search_engine = SearchEngine()

    # Add documents to the database
    search_engine.add_document("After the medication, headache and nausea were reported by the patient.")
    search_engine.add_document("The patient reported nausea and dizziness caused by the medication.")
    search_engine.add_document("Headache and dizziness are common effects of this medication.")
    search_engine.add_document("The medication caused a headache and nausea, but no dizziness was reported.")

    # Generate the inverted index
    search_engine.generate_inverted_index()

    # Perform searches with different queries
    print("Query: nausea and dizziness")
    search_engine.rank_documents("nausea and dizziness")  
    print("\nQuery: effects")
    search_engine.rank_documents("effects")  
    print("\nQuery: nausea was reported")
    search_engine.rank_documents("nausea was reported") 
    print("\nQuery: dizziness")
    search_engine.rank_documents("dizziness")  
    print("\nQuery: the medication")
    search_engine.rank_documents("the medication")  
