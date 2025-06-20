import pandas as pd
from datetime import datetime
from config.config import RATINGS_FILE

class UserHistory:
    def __init__(self):
        self.movielens_history = pd.DataFrame()
        self.additional_history = pd.DataFrame()
        self.combined_history = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """Load both MovieLens history and additional app history"""
        # Load MovieLens ratings as historical watch history
        self.load_movielens_history()
        
        # Load additional history from app interactions
        self.load_additional_history()
        
        # Combine both histories
        self.combine_histories()

    def load_movielens_history(self):
        """Load actual MovieLens ratings as watch history"""
        try:
            ratings_df = pd.read_csv(RATINGS_FILE)
            
            # Convert timestamp from Unix timestamp to readable format
            if 'timestamp' in ratings_df.columns:
                ratings_df['timestamp'] = pd.to_datetime(ratings_df['timestamp'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
                ratings_df['source'] = 'movielens'  # Mark source
            else:
                ratings_df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ratings_df['source'] = 'movielens'
            
            self.movielens_history = ratings_df[['userId', 'movieId', 'timestamp', 'rating', 'source']].copy()
            print(f"Loaded {len(self.movielens_history)} MovieLens ratings")
            
        except Exception as e:
            print(f"Error loading MovieLens history: {e}")
            self.movielens_history = pd.DataFrame(columns=['userId', 'movieId', 'timestamp', 'rating', 'source'])

    def load_additional_history(self):
        """Load additional history from app interactions"""
        try:
            self.additional_history = pd.read_csv('data/user_history.csv')
            if 'source' not in self.additional_history.columns:
                self.additional_history['source'] = 'app'
            print(f"Loaded {len(self.additional_history)} additional watch records")
        except FileNotFoundError:
            self.additional_history = pd.DataFrame(columns=['userId', 'movieId', 'timestamp', 'rating', 'source'])
            print("No additional history file found - starting fresh")

    def combine_histories(self):
        """Combine MovieLens and additional histories"""
        if self.movielens_history.empty and self.additional_history.empty:
            self.combined_history = pd.DataFrame(columns=['userId', 'movieId', 'timestamp', 'rating', 'source'])
        elif self.movielens_history.empty:
            self.combined_history = self.additional_history.copy()
        elif self.additional_history.empty:
            self.combined_history = self.movielens_history.copy()
        else:
            self.combined_history = pd.concat([self.movielens_history, self.additional_history], ignore_index=True)
        
        # Remove duplicates (same user + movie combination, keep most recent)
        self.combined_history = self.combined_history.sort_values('timestamp', ascending=False)
        self.combined_history = self.combined_history.drop_duplicates(subset=['userId', 'movieId'], keep='first')

    def add_to_history(self, user_id, movie_id, rating=None):
        """Add new watch history when 'Mark as Watched' is clicked"""
        new_entry = {
            'userId': int(user_id),
            'movieId': int(movie_id),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rating': rating,
            'source': 'app'
        }
        
        # Add to additional history
        self.additional_history = pd.concat([self.additional_history, pd.DataFrame([new_entry])], ignore_index=True)
        
        # Save to CSV
        self.save_additional_history()
        
        # Update combined history
        self.combine_histories()
        
        print(f"Added movie {movie_id} to history for user {user_id}")

    def get_user_history(self, user_id, limit=10):
        """Get complete watch history for a user"""
        user_history = self.combined_history[self.combined_history['userId'] == user_id]
        
        if not user_history.empty:
            user_history = user_history.sort_values('timestamp', ascending=False)
        
        return user_history.head(limit)

    def save_additional_history(self):
        """Save additional history to CSV"""
        self.additional_history.to_csv('data/user_history.csv', index=False)

    def get_user_stats(self, user_id):
        """Get statistics for a user's watch history"""
        user_history = self.get_user_history(user_id, limit=None)
        
        if user_history.empty:
            return {
                'total_movies': 0,
                'avg_rating': 0,
                'movielens_count': 0,
                'app_count': 0,
                'latest_watch': None
            }
        
        # Count by source
        movielens_count = len(user_history[user_history['source'] == 'movielens'])
        app_count = len(user_history[user_history['source'] == 'app'])
        
        # Calculate average rating (only for non-null ratings)
        ratings = user_history['rating'].dropna()
        avg_rating = ratings.mean() if len(ratings) > 0 else 0
        
        return {
            'total_movies': len(user_history),
            'avg_rating': avg_rating,
            'movielens_count': movielens_count,
            'app_count': app_count,
            'latest_watch': user_history.iloc[0]['timestamp'] if not user_history.empty else None
        }