from flask import Flask, request, render_template
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

NUM_OF_RECOMMENDATIONS_TO_RETURN = 30

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
    top_indices = genre_similarity.argsort()[::-1][1:NUM_OF_RECOMMENDATIONS_TO_RETURN]  # Exclude the first, as it's the input itself
    
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

@app.route('/login')
def about():
    return render_template('login.html', error=False)

@app.route('/user', methods=['POST'])
def user():
    try:
        # Retrieving the user ID from the form
        user_id = int(request.form['userId'])
        
        # Load user DataFrame
        user_dataframe = pd.read_csv("../dataset/ml-100k/u.data", names=['userId', 'item id', 'rating', 'timestamp'], delimiter="\t")

        print(user_id, file=sys.stdout)

        # Check if user_id exists in the dataframe
        if user_id in user_dataframe['userId'].values:
            print("Is in Dataset")
            return render_template('user.html', user_id=user_id)
        else:
            print("NOT in Dataset")
            return render_template('login.html', error=True)
        
    except (KeyError, ValueError) as e:
        # Handle errors such as missing key in form or inability to convert to integer
        print("Error:", e)
        return render_template('login.html', error=True)
    except Exception as e:
        # Handle other unexpected errors
        print("Unexpected Error:", e)
        return render_template('login.html', error=True)

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
