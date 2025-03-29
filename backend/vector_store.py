import json
import numpy as np

class VectorDB:
    def __init__(self, filename="vectors.json"):
        """
        Initialize the vector database.
        """
        self.filename = filename
        self.vectors = []
        self.texts = []
        
        # Load existing vectors if the file exists
        self.load_vectors()
    
    def add_vectors(self, texts, embeddings):
        """
        Add vectors and their corresponding texts to the database.
        """
        for text, embedding in zip(texts, embeddings):
            # Ensure embedding is a numpy array
            embedding = np.array(embedding)
            self.vectors.append(embedding)
            self.texts.append(text)
        
        # Save to JSON file after adding
        self.save_vectors()
    
    def save_vectors(self):
        """
        Save vectors and corresponding texts into a JSON file.
        """
        data = [{"text": text, "embedding": embedding.tolist()} for text, embedding in zip(self.texts, self.vectors)]
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def load_vectors(self):
        """
        Load vectors and texts from the JSON file if it exists.
        """
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            self.texts = [item["text"] for item in data]
            self.vectors = [np.array(item["embedding"]) for item in data]
        except FileNotFoundError:
            pass  # If file doesn't exist, start with empty vectors

    def get_vectors(self):
        """
        Return vectors as numpy arrays for processing.
        """
        return np.array(self.vectors)

    def get_texts(self):
        """
        Return texts for inspection.
        """
        return self.texts
