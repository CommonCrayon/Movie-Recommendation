import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

NUM_OF_RECOMMENDATIONS_TO_RETURN = 30



import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

def get_predicted_rating_for_movie(user_id, ratings_dataset, movie_dataset, top_n=5, top_predicted=30):
    # Fetch ratings data for all users
    ratings_data = pd.DataFrame(ratings_dataset, columns=['user_id', 'item_id', 'rating', 'timestamp'])

    # Fetch movie data
    movie_data = pd.DataFrame(movie_dataset, columns=["item_id", "title", "release date", 
                                        "video release date", "IMDb URL", "unknown", 
                                        "Action", "Adventure", "Animation",
                                        "Childrens", "Comedy", "Crime",
                                        "Documentary", "Drama", "Fantasy",
                                        "Film-Noir", "Horror", "Musical",
                                        "Mystery", "Romance", "Sci-Fi",
                                        "Thriller", "War", "Western"
                                        ])

    # Convert to sparse matrix
    user_item_matrix = ratings_data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    user_item_matrix_sparse = csr_matrix(user_item_matrix.values)

    # Calculate cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(user_item_matrix_sparse)
    utility_matrix = ratings_data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)

    # Similarity scores for the given user
    user_similarity_scores = cosine_sim_matrix[user_id]

    # Top N similar users (excluding the user itself)
    similar_users_indices = np.argsort(user_similarity_scores)[::-1][1:top_n+1]

    # Dictionary to store aggregated ratings from similar users
    predicted_ratings = {}

    # Unrated items by the given user
    unrated_items = utility_matrix.loc[user_id][utility_matrix.loc[user_id] == 0].index

    for item_id in unrated_items:
        # Ratings of unrated items by similar users
        similar_user_ratings = utility_matrix.iloc[similar_users_indices][item_id]

        # Weighted sum and sum of weights
        weighted_sum = np.dot(similar_user_ratings, user_similarity_scores[similar_users_indices])
        sum_of_weights = np.sum(user_similarity_scores[similar_users_indices])

        # Predicted rating if sum_of_weights is not zero
        if sum_of_weights != 0:
            predicted_ratings[item_id] = weighted_sum / sum_of_weights

    # Sort predicted ratings and return top 30 items with titles
    top_predicted_items = sorted(predicted_ratings.items(), key=lambda x: x[1], reverse=True)[:top_predicted]

    # Get titles for top predicted items
    top_predicted_items_with_titles = []
    for item_id, predicted_rating in top_predicted_items:
        title = movie_data[movie_data['item_id'] == item_id]['title'].values[0]
        top_predicted_items_with_titles.append({'item_id': item_id, 'title': title, 'predicted_rating': predicted_rating})

    return top_predicted_items_with_titles

