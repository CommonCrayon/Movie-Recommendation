from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

number_of_recommendations_to_return = 30


app = Flask(__name__)

def extract_genres(row):
    genres_columns = ["Action", "Adventure", "Animation", "Children's", 
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
    top_indices = genre_similarity.argsort()[::-1][1:number_of_recommendations_to_return]  # Exclude the first, as it's the input itself
    
    # Get the movie titles and similarity scores
    recommended_movies = movies_dataframe.iloc[top_indices][['title']].copy()
    recommended_movies['similarity_score'] = genre_similarity[top_indices]
    
    return recommended_movies.reset_index()

# Function to generate movie recommendations based on selected genres
def generate_recommendations(selected_genres):
    movies_dataframe = pd.read_csv("../dataset/ml-100k/u.item", delimiter="|", encoding="latin1",
                                names=["item id", "title", "release date", 
                                        "video release date", "IMDb URL", "unknown", 
                                        "Action", "Adventure", "Animation",
                                        "Children's", "Comedy", "Crime",
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

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    selected_genres = request.form.getlist('genres')
    print("Selected genres:", selected_genres)
    
    # Call the function to generate recommendations
    recommendations = generate_recommendations(selected_genres)
    
    # Pass recommendations to the template
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
