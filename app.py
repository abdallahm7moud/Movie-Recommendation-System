import dash
from dash import html, dcc, Input, Output, State, ALL, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from models.recommender import MovieRecommender
from models.similarity import ItemSimilarity
from models.tmdb_api import TMDBApi
from models.user_history import UserHistory
from utils.helpers import create_movie_card, create_loading_spinner, create_history_card

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize TMDB API
tmdb_api = TMDBApi()

# Initialize models
recommender = MovieRecommender(tmdb_api)
similarity_model = ItemSimilarity(tmdb_api)
user_history = UserHistory()

# Load data
recommender.load_data()
similarity_model.load_data()

# Layout
app.layout = html.Div([
    dbc.NavbarSimple(
        brand="Movie Recommender System",
        brand_href="#",
        color="dark",
        dark=True,
    ),
    
    dbc.Container([
        dbc.Tabs([
            dbc.Tab(label="User Recommendations", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("User Selection", className="mt-3"),
                        dcc.Dropdown(
                            id='user-dropdown',
                            options=[{'label': f"User {i}", 'value': i} 
                                   for i in recommender.ratings_df['userId'].unique()],
                            value=1
                        ),
                        html.H4("Number of Recommendations", className="mt-3"),
                        dcc.Input(
                            id='n-recommendations',
                            type='number',
                            value=6,
                            min=1,
                            max=20
                        ),
                        html.Button('Get Recommendations', 
                                  id='get-recommendations-button', 
                                  className="mt-3 btn btn-primary"),
                        
                        # Watch History Section
                        html.Hr(className="mt-4"),
                        html.H4("Watch History", className="mt-3"),
                        html.P("History Limit", className="mb-2"),
                        dcc.Input(
                            id='history-limit',
                            type='number',
                            value=6,
                            min=1,
                            max=20
                        ),
                        html.Button('View History', 
                                  id='get-history-button', 
                                  className="mt-3 btn btn-secondary"),
                    ], width=3),
                    
                    dbc.Col([
                        # Single output div that will show either recommendations OR history
                        html.Div(id='main-content-output', className="mt-3")
                    ], width=9)
                ])
            ]),
            
            dbc.Tab(label="Item Similarity", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Movie Selection", className="mt-3"),
                        dcc.Dropdown(
                            id='movie-dropdown',
                            options=[{'label': row['title'], 'value': row['movieId']} 
                                   for _, row in recommender.movies_df.iterrows()],
                            value=1
                        ),
                        html.H4("Number of Similar Movies", className="mt-3"),
                        dcc.Input(
                            id='n-similar',
                            type='number',
                            value=6,
                            min=1,
                            max=20
                        ),
                        html.Button('Find Similar Movies', 
                                  id='get-similar-button', 
                                  className="mt-3 btn btn-primary"),
                    ], width=3),
                    dbc.Col([
                        html.Div(id='similarity-output', className="mt-3")
                    ], width=9)
                ])
            ])
        ])
    ], className="mt-4"),
    
    # Hidden div to store current user for watch buttons
    html.Div(id='current-user', style={'display': 'none'}),
    
    # Toast for notifications
    dbc.Toast(
        id="watch-toast",
        header="Movie Added to History!",
        is_open=False,
        dismissable=True,
        duration=3000,
        icon="success",
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index": 1},
    ),
    
    create_loading_spinner()
])

# Store current user when recommendations are loaded
@app.callback(
    Output('current-user', 'children'),
    [Input('get-recommendations-button', 'n_clicks'),
     Input('get-history-button', 'n_clicks')],
    [State('user-dropdown', 'value')]
)
def store_current_user(rec_clicks, hist_clicks, user_id):
    return user_id

# Main content callback - handles both recommendations and history
@app.callback(
    Output('main-content-output', 'children'),
    [Input('get-recommendations-button', 'n_clicks'),
     Input('get-history-button', 'n_clicks')],
    [State('user-dropdown', 'value'),
     State('n-recommendations', 'value'),
     State('history-limit', 'value')]
)
def update_main_content(rec_clicks, hist_clicks, user_id, n_recommendations, history_limit):
    ctx = callback_context
    
    if not ctx.triggered:
        return html.P("Select an option above to see content.", className="text-muted mt-4")
    
    # Determine which button was clicked
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'get-recommendations-button' and rec_clicks:
        # Show recommendations only
        recommendations = recommender.get_top_n_recommendations(user_id, n_recommendations or 6)
        
        return html.Div([
            html.H4("Recommended Movies", className="mb-4"),
            dbc.Row([
                dbc.Col(create_movie_card(movie), width=4)
                for movie in recommendations
            ])
        ])
    
    elif trigger_id == 'get-history-button' and hist_clicks:
        # Show history only
        return get_user_history_display(user_id, history_limit or 6)
    
    return html.P("Click a button above to see content.", className="text-muted mt-4")

@app.callback(
    Output('similarity-output', 'children'),
    [Input('get-similar-button', 'n_clicks')],
    [State('movie-dropdown', 'value'),
     State('n-similar', 'value')]
)
def update_similar_movies(n_clicks, movie_id, n):
    if n_clicks is None:
        return html.P("Select a movie and click 'Find Similar Movies' to see recommendations.", 
                     className="text-muted")
    
    similar_movies = similarity_model.get_similar_movies(movie_id, n)
    
    return [
        html.H4("Similar Movies", className="mb-4"),
        dbc.Row([
            dbc.Col(create_movie_card(movie, show_watch_button=False), width=4)
            for movie in similar_movies
        ])
    ]

# Handle watch button clicks
@app.callback(
    [Output('watch-toast', 'is_open'),
     Output('main-content-output', 'children', allow_duplicate=True)],
    [Input({'type': 'watch-button', 'index': ALL}, 'n_clicks')],
    [State('current-user', 'children'),
     State('history-limit', 'value')],
    prevent_initial_call=True
)
def handle_watch_button(n_clicks_list, current_user, history_limit):
    if not any(n_clicks_list) or not current_user:
        return False, dash.no_update
    
    # Get which button was clicked
    ctx = callback_context
    if not ctx.triggered:
        return False, dash.no_update
    
    # Extract movie ID from the triggered button
    button_id = ctx.triggered[0]['prop_id']
    movie_id = eval(button_id.split('.')[0])['index']
    
    # Add to user history
    user_history.add_to_history(current_user, movie_id)
    
    # Keep showing recommendations (don't switch to history)
    recommendations = recommender.get_top_n_recommendations(current_user, 6)
    updated_content = html.Div([
        html.H4("Recommended Movies", className="mb-4"),
        dbc.Row([
            dbc.Col(create_movie_card(movie), width=4)
            for movie in recommendations
        ])
    ])
    
    return True, updated_content

def get_user_history_display(user_id, limit):
    """Helper function to generate history display"""
    history = user_history.get_user_history(user_id, limit)
    
    if history.empty:
        return html.Div([
            html.H4(f"Watch History for User {user_id}", className="mb-3"),
            dbc.Alert([
                html.H5("No watch history found!", className="alert-heading"),
                html.P("This user hasn't rated any movies yet.")
            ], color="info")
        ])
    
    # Get user stats
    stats = user_history.get_user_stats(user_id)
    
    history_movies = []
    for _, record in history.iterrows():
        # Get movie details
        movie_info = recommender.movies_df[recommender.movies_df['movieId'] == record['movieId']]
        if not movie_info.empty:
            movie_data = movie_info.iloc[0]
            tmdb_info = tmdb_api.search_movie(movie_data['title'])
            
            movie_details = {
                'movieId': record['movieId'],
                'title': movie_data['title'],
                'genres': movie_data['genres'],
                'watched_on': record['timestamp'],
                'user_rating': record['rating'] if pd.notna(record['rating']) else None,
                'source': record.get('source', 'unknown'),
                **tmdb_info
            }
            history_movies.append(movie_details)
    
    return html.Div([
        html.H4(f"Watch History for User {user_id}", className="mb-3"),
        # User stats
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{stats.get('total_movies', 0)}", className="card-title text-primary"),
                        html.P("Movies Watched", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{stats.get('avg_rating', 0):.1f}/5" if stats.get('avg_rating', 0) > 0 else "N/A", 
                               className="card-title text-success"),
                        html.P("Average Rating", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{stats.get('movielens_count', 0)}", className="card-title text-info"),
                        html.P("From MovieLens", className="card-text")
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5(f"{stats.get('app_count', 0)}", className="card-title text-success"),
                        html.P("Recently Watched", className="card-text")
                    ])
                ])
            ], width=3),
        ], className="mb-4"),
        
        # Movie cards
        dbc.Row([
            dbc.Col([
                create_history_card(movie),
                html.P(f"Watched: {movie['watched_on']}", 
                      className="text-muted text-center small mt-2")
            ], width=4)
            for movie in history_movies
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug=True)