import requests
import time
from datetime import datetime, timedelta
from config.config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL

class TMDBApi:
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.image_base_url = TMDB_IMAGE_BASE_URL
        self.cache = {}
        self.cache_timestamps = {}

    def _is_cache_valid(self, key):
        if key not in self.cache_timestamps:
            return False
        return (datetime.now() - self.cache_timestamps[key]).seconds < 3600

    def search_movie(self, movie_title):
        # Check cache first
        if movie_title in self.cache and self._is_cache_valid(movie_title):
            return self.cache[movie_title]

        try:
            clean_title = movie_title.split('(')[0].strip()
            
            endpoint = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': clean_title,
                'language': 'en-US'
            }
            
            response = requests.get(endpoint, params=params)
            data = response.json()
            
            if data.get('results'):
                movie_data = data['results'][0]
                poster_path = movie_data.get('poster_path')
                if poster_path:
                    poster_url = f"{self.image_base_url}{poster_path}"
                else:
                    poster_url = "https://via.placeholder.com/500x750?text=No+Poster+Available"
                
                # Additional movie details
                movie_info = {
                    'poster_url': poster_url,
                    'overview': movie_data.get('overview', ''),
                    'release_date': movie_data.get('release_date', ''),
                    'vote_average': movie_data.get('vote_average', 0)
                }
            else:
                movie_info = {
                    'poster_url': "https://via.placeholder.com/500x750?text=No+Poster+Available",
                    'overview': '',
                    'release_date': '',
                    'vote_average': 0
                }

            # Update cache
            self.cache[movie_title] = movie_info
            self.cache_timestamps[movie_title] = datetime.now()
            
            time.sleep(0.1)  # Rate limiting
            return movie_info

        except Exception as e:
            print(f"Error fetching movie data for {movie_title}: {str(e)}")
            return {
                'poster_url': "https://via.placeholder.com/500x750?text=Error+Loading+Poster",
                'overview': '',
                'release_date': '',
                'vote_average': 0
            }