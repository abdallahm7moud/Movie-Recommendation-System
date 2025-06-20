

# MovieLens Recommender Dashboard

This is an interactive movie recommendation dashboard built with [Dash](https://dash.plotly.com/) and powered by collaborative filtering and content-based models. It offers personalized movie recommendations, item similarity browsing, and interactive UI features such as watch history logging and theming support.

---

## 🎬 Demo

A video demonstration of the dashboard is available

### 📽 Watch the Demo :

https://github.com/user-attachments/assets/b9f30706-33e3-4532-bcbc-81b161617798

---

## Features

### User Page

- **User Selection**: Choose a user from the MovieLens dataset.
- **Watch History View**: Displays the selected user's past watched movies with TMDB-enhanced visuals and metadata.
- **Number of Recommendations Input**: Control how many top-N movies to recommend.
- **Top-N Recommendations**: Returns a ranked list of personalized recommendations for the selected user.
- **Recommendation Pagination**: Navigate through the list of recommendations using offset paging logic.
- **Mark as Watched**: Adds a movie to the user’s watch history interactively.

### Item Page

- **Movie Selection**: Choose any movie from the dataset.
- **Movie Profile View**: Shows movie title, genres, and enriched details from TMDB (e.g., poster, overview).
- **Top-N Similar Movies**: Displays the most similar movies to the selected one based on genre similarity.
- **Similarity Navigation**: Move forward/backward across pages of similar movies using offset.

---

## Recommender Models

### User Recommender

- Uses the `SVD` algorithm from the [Surprise](https://surpriselib.com/) library.
- Predicts ratings for unseen movies based on matrix factorization.
- The trained model is loaded and used in real-time to serve top-N personalized recommendations.

### Item Similarity

- Applies `TfidfVectorizer` on genre metadata to generate feature vectors.
- Uses `cosine_similarity` to compute similarity scores between movies.
- Similar items are retrieved dynamically on user selection.

---

## TMDB Integration

This project uses the [TMDB API](https://developer.themoviedb.org/docs) to fetch:

- Movie posters
- Overviews and additional metadata
- Optional: Used for both recommendation and history sections to improve visual appeal

---

## Dataset

- **Source**: [MovieLens Small Dataset](https://grouplens.org/datasets/movielens/)
- **Size**: ~100,000 ratings across ~9000 movies
- Used primarily for collaborative filtering (ratings matrix) and content-based filtering (genres).

---

## Application Structure

```
├── app.py                 # Main Dash app entry point
├── assets/
│   ├── styles.css         # Dark theme CSS (IMDb-style)
│   └── light_styles.css   # Light theme CSS
├── models/
│   ├── recommender.py     # SVD model logic (Surprise)
│   ├── similarity.py      # TF-IDF + cosine similarity
│   ├── tmdb_api.py        # TMDB API client
│   └── user_history.py    # Watch history logging
├── utils/
│   └── helpers.py         # UI card generation, loading spinners, etc.
├── data/                  # MovieLens dataset (processed)
├── config/                # Configs and keys (if any)
├── README.md
└── requirements.txt
```

---

## How to Run the App

1. **Clone the repository** :
   ```bash
   git clone https://github.com/your-username/movielens-recommender.git
   cd movielens-recommender
   ```
   
2. **Create and activate a virtual environment (optional but recommended)** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API keys** :

   Copy `.env.example` to `.env` and fill in required keys.
   
   ```bash
   cp .env.example .env
   ```

5. **Run the app** :
   ```bash
   python app.py
   ```

6. **Access the app** :
   Navigate to [http://localhost:8050](http://localhost:8050) in your web browser.

---
