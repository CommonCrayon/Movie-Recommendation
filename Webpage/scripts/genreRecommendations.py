from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

NUM_OF_RECOMMENDATIONS_TO_RETURN = 31

def extract_genres(row):
    genres_columns = ["Action", "Adventure", "Animation", "Childrens", 
                "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
                "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
                "Sci-Fi", "Thriller", "War", "Western"]
        
    genres = [col for col in genres_columns if row[col] == 1]
    return ' '.join(genres)

def get_recommendations_genre(genres, vectorizer, genre_matrix, movies_dataframe):
    # Convert the list of genres into a single string
    genres_string = ' '.join(genres)
    
    # Vectorize the provided genres
    genres_vector = vectorizer.transform([genres_string])
    
    # Calculate similarity with all movies
    genre_similarity = cosine_similarity(genres_vector, genre_matrix).flatten()
    
    # Get indices of top similar movies
    top_indices = genre_similarity.argsort()[::-1][1:NUM_OF_RECOMMENDATIONS_TO_RETURN]  # Exclude the first, as it's the input itself
    
    # Filter out movies with similarity score of 0
    nonzero_indices = [index for index in top_indices if genre_similarity[index] != 0]
    
    # Get the movie titles and similarity scores
    recommended_movies = movies_dataframe.iloc[nonzero_indices][['title']].copy()
    recommended_movies['similarity_score'] = genre_similarity[nonzero_indices]
    recommended_movies['genres'] = movies_dataframe.iloc[nonzero_indices]['genres']  # Add genres column
    recommended_movies['genres'] = recommended_movies['genres'].str.replace(' ', ', ')

    return recommended_movies.reset_index()


# Function to generate movie recommendations based on selected genres
def genre_recommendations(selected_genres, movie_dataset):
    movies_dataframe = pd.DataFrame(movie_dataset,
                                columns=["item_id", "title", "release_date", 
                                            "video_release_date", "IMDb_URL", "unknown", 
                                            "Action", "Adventure", "Animation",
                                            "Childrens", "Comedy", "Crime",
                                            "Documentary", "Drama", "Fantasy",
                                            "Film-Noir", "Horror", "Musical",
                                            "Mystery", "Romance", "Sci-Fi",
                                            "Thriller", "War", "Western"
                                        ])
    movies_dataframe = movies_dataframe.drop(["unknown"], axis=1)
    movies_dataframe['genres'] = movies_dataframe.apply(extract_genres, axis=1)

    # Vectorization
    vectorizer = CountVectorizer(binary=True, lowercase=False)
    genre_matrix = vectorizer.fit_transform(movies_dataframe['genres'])

    return get_recommendations_genre(selected_genres, vectorizer, genre_matrix, movies_dataframe)