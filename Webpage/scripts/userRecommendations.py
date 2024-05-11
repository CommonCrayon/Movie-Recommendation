import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import time

NUM_OF_RECOMMENDATIONS_TO_RETURN = 30


def get_user_data(user_id):
    # Read the dataset into a DataFrame
    user_dataframe = pd.read_csv("Dataset/Working/u.user", names=['user id', 'age', 'gender', 'occupation', 'zip code'], delimiter="|")

    # Filter the DataFrame to find the record with the given user ID
    filtered_data = user_dataframe[user_dataframe['user id'] == user_id]

    # Convert gender to 'Male' or 'Female'
    filtered_data.loc[:, 'gender'] = filtered_data['gender'].map({'M': 'Male', 'F': 'Female'}).fillna(filtered_data['gender'])

    # Capitalize the first letter of occupation
    filtered_data.loc[:, 'occupation'] = filtered_data['occupation'].str.capitalize()

    # Return the modified DataFrame
    return filtered_data.reset_index()



def user_recommendations(user_id):

    # Let's assume you have another dataset containing movie information like movie_id, title, genres
    movies_dataframe = pd.read_csv("./Dataset/Working/u.item", delimiter="|", encoding="latin1",
                                names=["item id", "title", "release date", 
                                        "video release date", "IMDb URL", "unknown", 
                                        "Action", "Adventure", "Animation",
                                        "Children's", "Comedy", "Crime",
                                        "Documentary", "Drama", "Fantasy",
                                        "Film-Noir", "Horror", "Musical",
                                        "Mystery", "Romance", "Sci-Fi",
                                        "Thriller", "War", "Western"
                                        ])
    movies_dataframe = movies_dataframe.drop(["release date", "video release date", "IMDb URL",
                        "unknown", "Action", "Adventure", "Animation",
                        "Children's", "Comedy", "Crime", "Documentary",
                        "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
                        "Mystery", "Romance", "Sci-Fi","Thriller", "War", "Western"], axis=1)


    # Reading the dataset
    userbase1_dataframe = pd.read_csv("./Dataset/Working/u.data", names=['user id', 'item id', 'rating', 'timestamp'], delimiter="\t")
    userbase1_dataframe = userbase1_dataframe.drop(["timestamp"], axis=1)


    # Convert DataFrame to sparse matrix
    user_item_matrix = userbase1_dataframe.pivot(index='user id', columns='item id', values='rating').fillna(0)
    user_item_matrix_sparse = csr_matrix(user_item_matrix.values)

    # Calculate cosine similarity matrix
    cosine_sim_matrix = cosine_similarity(user_item_matrix_sparse)


    utility_matrix = userbase1_dataframe.pivot(index='user id', columns='item id', values='rating').fillna(0)

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
    recommended_items_df = movies_dataframe[movies_dataframe['item id'].isin(recommended_items)].copy()
    
    # Add aggregated scores to the DataFrame using .loc accessor
    recommended_items_df.loc[:, 'aggregated_score'] = [aggregated_ratings[item_id] for item_id in recommended_items_df['item id']]
    
    # Sort dataframe by aggregated_score in descending order
    recommended_items_df = recommended_items_df.sort_values(by='aggregated_score', ascending=False).reset_index(drop=True)
    
    return recommended_items_df



def update_u_data(user_id, item_id, rating):
    # Read the existing u.data file
    user_dataframe = pd.read_csv("./Dataset/Working/u.data", names=['user id', 'item id', 'rating', 'timestamp'], delimiter="\t")
    

    index_to_replace = user_dataframe[(user_dataframe['user id'] == user_id) & (user_dataframe['item id'] == item_id)].index

    if not index_to_replace.empty:
        user_dataframe.loc[index_to_replace, ['user id', 'item id', 'rating', 'timestamp']] = [user_id, item_id, rating, int(time.time())]
    else:
        user_dataframe.loc[len(user_dataframe)] = [user_id, item_id, rating, int(time.time())]


    # Save the updated u.data file
    user_dataframe.to_csv("./Dataset/Working/u.data", header=False, index=False, sep='\t')
    
    print("u.data updated successfully.")