import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TMDB API Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Data paths
MOVIES_FILE = "data/movies.csv"
RATINGS_FILE = "data/ratings.csv"

# Model parameters
SVD_PARAMS = {
    'n_factors': 100,
    'n_epochs': 20,
    'lr_all': 0.005,
    'reg_all': 0.02
}

# Cache configuration
CACHE_EXPIRY = 3600  # 1 hour in seconds