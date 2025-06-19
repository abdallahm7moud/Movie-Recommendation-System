import dash_bootstrap_components as dbc
from dash import html

def create_movie_card(movie, show_watch_button=True):
    card_body_children = [
        html.H5(movie['title'], className="card-title")
    ]
    
    # Add rating information based on what's available
    if 'predicted_rating' in movie:
        card_body_children.append(
            html.P(f"Predicted Rating: {movie['predicted_rating']}", className="card-text text-success")
        )
    elif 'similarity_score' in movie:
        card_body_children.append(
            html.P(f"Similarity: {movie['similarity_score']}", className="card-text text-info")
        )
    elif 'user_rating' in movie and movie['user_rating'] and str(movie['user_rating']) != 'nan':
        card_body_children.append(
            html.P(f"Your Rating: ⭐ {movie['user_rating']}/5", className="card-text text-warning font-weight-bold")
        )
    
    # Add common movie information
    card_body_children.extend([
        html.P(f"Genres: {movie['genres']}", className="card-text text-muted"),
        html.P(movie['overview'][:200] + '...' if len(movie.get('overview', '')) > 200 else movie.get('overview', ''),
              className="card-text description"),
        html.P(f"Release Date: {movie.get('release_date', 'N/A')}", className="card-text text-muted"),
        html.P(f"TMDB Rating: {movie.get('vote_average', 0)}/10", className="card-text rating")
    ])
    
    # Add watch button if enabled
    if show_watch_button:
        movie_id = int(movie['movieId'])
        card_body_children.append(
            dbc.Button(
                "Mark as Watched", 
                id={'type': 'watch-button', 'index': movie_id},
                className="btn btn-primary mt-2",
                size="sm"
            )
        )
    
    return dbc.Card([
        dbc.CardImg(src=movie.get('poster_url', 'https://via.placeholder.com/500x750?text=No+Image'), top=True),
        dbc.CardBody(card_body_children)
    ], className="mb-4 h-100")

def create_history_card(movie):
    """Create a card specifically for watch history"""
    source_badge = dbc.Badge(
        "MovieLens" if movie.get('source') == 'movielens' else "Recently Watched",
        color="info" if movie.get('source') == 'movielens' else "success",
        className="mb-2"
    )
    
    return dbc.Card([
        dbc.CardImg(src=movie.get('poster_url', 'https://via.placeholder.com/500x750?text=No+Image'), top=True),
        dbc.CardBody([
            source_badge,
            html.H5(movie['title'], className="card-title"),
            html.P(f"Your Rating: ⭐ {movie['user_rating']}/5" if movie.get('user_rating') and str(movie['user_rating']) != 'nan' else "Not Rated", 
                   className="card-text text-warning font-weight-bold"),
            html.P(f"Genres: {movie['genres']}", className="card-text text-muted"),
            html.P(movie.get('overview', '')[:150] + '...' if len(movie.get('overview', '')) > 150 else movie.get('overview', ''),
                  className="card-text description"),
            html.P(f"TMDB Rating: {movie.get('vote_average', 0)}/10", className="card-text rating")
        ])
    ], className="mb-4 h-100")

def create_loading_spinner():
    return dbc.Spinner(
        children=[html.Div(id="loading-output")],
        size="lg",
        color="primary",
        type="border",
        fullscreen=True,
    )