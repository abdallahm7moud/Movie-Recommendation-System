from surprise import Dataset, Reader, SVD
import pandas as pd
from config.config import SVD_PARAMS, MOVIES_FILE, RATINGS_FILE

class MovieRecommender:
    def __init__(self, tmdb_api):
        self.model = SVD(**SVD_PARAMS)
        self.movies_df = None
        self.ratings_df = None
        self.tmdb_api = tmdb_api
        
    def load_data(self):
        self.movies_df = pd.read_csv(MOVIES_FILE)
        self.ratings_df = pd.read_csv(RATINGS_FILE)
        
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(self.ratings_df[['userId', 'movieId', 'rating']], reader)
        
        trainset = data.build_full_trainset()
        self.model.fit(trainset)
        
    def get_top_n_recommendations(self, user_id, n=10, offset=0):
        all_movies = self.movies_df['movieId'].unique()
        predictions = [self.model.predict(user_id, movie_id) for movie_id in all_movies]
        predictions.sort(key=lambda x: x.est, reverse=True)
        recommendations = predictions[offset:offset + n]
        
        detailed_recommendations = []
        for pred in recommendations:
            movie_info = self.movies_df[self.movies_df['movieId'] == pred.iid].iloc[0]
            tmdb_info = self.tmdb_api.search_movie(movie_info['title'])
            
            detailed_recommendations.append({
                'movieId': int(pred.iid),  
                'title': movie_info['title'],
                'predicted_rating': round(pred.est, 2),
                'genres': movie_info['genres'],
                **tmdb_info
            })
            
        return detailed_recommendations