import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class CineVerseRecommender:
    def __init__(self):
        self.df = pd.read_csv("data/movies_final.csv")
        self.tfidf = pickle.load(open("data/tfidf_vectorizer.pkl", "rb"))
        self.cosine_sim = pickle.load(open("data/cosine_sim.pkl", "rb"))
        self.indices = pd.Series(
            self.df.index, index=self.df['title'].str.lower()
        ).drop_duplicates()
        print(f"✅ CineVerse loaded {len(self.df)} movies")

    def search_movies(self, query: str, limit: int = 10):
        query_lower = query.lower()
        mask = self.df['title'].str.lower().str.contains(query_lower, na=False)
        results = self.df[mask].head(limit)
        return results.to_dict('records')

    def get_recommendations(self, title: str, n: int = 10, filters: dict = None):
        title_lower = title.lower()
        
        if title_lower not in self.indices:
            matches = [t for t in self.indices.index if title_lower in t]
            if not matches:
                return {"error": "Movie not found", "results": []}
            title_lower = matches[0]
        
        idx = self.indices[title_lower]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n*3]  # Get extra for filtering
        
        movie_indices = [i[0] for i in sim_scores]
        results = self.df.iloc[movie_indices].copy()
        results['similarity'] = [round(s[1]*100, 1) for s in sim_scores]
        
        # Apply filters
        if filters:
            if filters.get('genre'):
                results = results[results['genres'].str.contains(
                    filters['genre'], case=False, na=False)]
            if filters.get('year_from'):
                results = results[results['release_year'].astype(str) >= str(filters['year_from'])]
            if filters.get('min_rating'):
                results = results[results['rating'] >= float(filters['min_rating'])]
        
        return {
            "source_movie": title,
            "results": results.head(n).to_dict('records')
        }

    def get_movie_by_id(self, movie_id: int):
        movie = self.df[self.df['id'] == movie_id]
        if movie.empty:
            return None
        return movie.iloc[0].to_dict()

    def get_trending(self, n: int = 20):
        trending = self.df.nlargest(n, 'vote_count')
        return trending.to_dict('records')

    def get_by_genre(self, genre: str, n: int = 20):
        filtered = self.df[self.df['genres'].str.contains(genre, case=False, na=False)]
        filtered = filtered.nlargest(n, 'rating')
        return filtered.to_dict('records')