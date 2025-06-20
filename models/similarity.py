from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from config.config import MOVIES_FILE

class ItemSimilarity:
    def __init__(self, tmdb_api):
        self.movies_df = None
        self.similarity_matrix = None
        self.tmdb_api = tmdb_api
        
    def load_data(self):
        self.movies_df = pd.read_csv(MOVIES_FILE)
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(self.movies_df['genres'].str.replace('|', ' ', regex=False))
        
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        
    def get_similar_movies(self, movie_id, n=10, offset=0):
        movie_idx = self.movies_df[self.movies_df['movieId'] == movie_id].index[0]
        similar_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        
        similar_scores = [
        (idx, score)
        for idx, score in similar_scores
        if idx != movie_idx
        ]
        
        similar_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)
        
        similar_movies = similar_scores[offset:offset + n]
        
        recommendations = []
        for idx, score in similar_movies:
            movie = self.movies_df.iloc[idx]
            tmdb_info = self.tmdb_api.search_movie(movie['title'])
            
            recommendations.append({
                'movieId': int(movie['movieId']),  
                'title': movie['title'],
                'similarity_score': round(score, 2),
                'genres': movie['genres'],
                **tmdb_info
            })
            
        return recommendations