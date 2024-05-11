import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

NUM_OF_RECOMMENDATIONS_TO_RETURN = 30


def user_recommendations(user_id, ratings_dataset, movie_dataset):
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


    # Convert DataFrame to sparse matrix
    user_item_matrix = ratings_data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)
    user_item_matrix_sparse = csr_matrix(user_item_matrix.values)

    # Calculate cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(user_item_matrix_sparse)


    utility_matrix = ratings_data.pivot(index='user_id', columns='item_id', values='rating').fillna(0)

    # Convert cosine similarity matrix to DataFrame for better visualization 
    # Where both the rows and columns are labeled with user ids, and the values represent the cosine similarity between corresponding users based on their ratings.
    cosine_sim_df = pd.DataFrame(cosine_sim_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)

    # Get cosine similarity scores for the given user
    user_similarity_scores = cosine_sim_df[user_id]
    
    # Sort users by similarity scores and get top N similar users (excluding the user itself)
    similar_users = user_similarity_scores.sort_values(ascending=False)[1:NUM_OF_RECOMMENDATIONS_TO_RETURN+1]
    
    # Initialize a dictionary to store aggregated ratings from similar users
    aggregated_ratings = {}
    
    # Aggregate ratings from similar users for items not yet rated by the given user
    for similar_user_id, similarity_score in similar_users.items():
        # Get items rated by the similar user that the given user has not yet rated
        unrated_items = utility_matrix.loc[user_id][utility_matrix.loc[user_id] == 0].index
        
        # Get ratings of unrated items by the similar user
        similar_user_ratings = utility_matrix.loc[similar_user_id, unrated_items]
        
        # Aggregate ratings from similar user
        for item_id, rating in similar_user_ratings.items():
            if item_id not in aggregated_ratings:
                aggregated_ratings[item_id] = 0
            aggregated_ratings[item_id] += rating * similarity_score
    
    # Sort recommended items by aggregated ratings
    recommended_items = sorted(aggregated_ratings, key=aggregated_ratings.get, reverse=True)[:NUM_OF_RECOMMENDATIONS_TO_RETURN]
    
    # Filter movies_dataframe to include only recommended items
    recommended_items_df = movie_data[movie_data['item_id'].isin(recommended_items)].copy()
    
    # Add aggregated scores to the DataFrame using .loc accessor
    recommended_items_df.loc[:, 'aggregated_score'] = [aggregated_ratings[item_id] for item_id in recommended_items_df['item_id']]
    
    # Sort dataframe by aggregated_score in descending order
    recommended_items_df = recommended_items_df.sort_values(by='aggregated_score', ascending=False).reset_index(drop=True)
    
    return recommended_items_df
