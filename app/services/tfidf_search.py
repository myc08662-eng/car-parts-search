import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.utils.transliterate import transliterate
from app.config import get_settings

settings = get_settings()

class TFIDFSearch:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.parts_data = []
        self.is_fitted = False

    def fit(self, parts_list):
        self.parts_data = parts_list
        texts = []
        for item in parts_list:
            car_latin = transliterate(item['car_name'])
            part_latin = transliterate(item['part_name'])
            cat_latin = transliterate(item.get('category', ''))
            texts.append(
                f"{item['part_name']} {item['car_name']} {item.get('category', '')} "
                f"{part_latin} {car_latin} {cat_latin}"
            )
        self.vectorizer = TfidfVectorizer(
            analyzer='char',
            ngram_range=(3, 5),
            lowercase=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)
        self.is_fitted = True

    def search_by_category(self, query: str, category: str = None, top_k: int = 30):
        if not self.is_fitted or len(query) < settings.SEARCH_MIN_QUERY_LEN:
            return []

        query_latin = transliterate(query)
        query_combined = f"{query} {query_latin}"
        query_vec = self.vectorizer.transform([query_combined.lower()])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k * 2]
        results = []
        for idx in top_indices:
            if similarities[idx] > settings.TFIDF_SIMILARITY_THRESHOLD:
                item = self.parts_data[idx].copy()
                item['similarity'] = float(similarities[idx])
                if not category or item.get('category', '').lower() == category.lower():
                    results.append(item)
                    if len(results) >= top_k:
                        break
        return results