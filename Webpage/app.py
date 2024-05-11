from flask import Flask, request, render_template
from scripts.genreRecommendations import genre_recommendations
from scripts.userRecommendations import user_recommendations
import sqlite3
import pandas as pd
from flask import g
import time

app = Flask(__name__)


def get_connection():
    if 'conn' not in g:
        g.conn = establish_connection()
    return g.conn

@app.teardown_appcontext
def close_connection(exception):
    conn = g.pop('conn', None)
    if conn is not None:
        conn.close()

def establish_connection():
    conn = sqlite3.connect("database.db")

    # USER DATASET
    try:
        user_dataset = pd.read_csv("Dataset/Working/u.user", names=['user_id', 'age', 'gender', 'occupation', 'zip_code'], delimiter="|")
        user_dataset.to_sql('user', conn, if_exists='fail', index=False)
    except:
        pass

    # MOVIE DATASET
    try:
        movies_dataset = pd.read_csv("./Dataset/Working/u.item", delimiter="|", encoding="latin1",
                                    names=["item_id", "title", "release_date", 
                                            "video_release_date", "IMDb_URL", "unknown", 
                                            "Action", "Adventure", "Animation",
                                            "Childrens", "Comedy", "Crime",
                                            "Documentary", "Drama", "Fantasy",
                                            "Film-Noir", "Horror", "Musical",
                                            "Mystery", "Romance", "Sci-Fi",
                                            "Thriller", "War", "Western"
                                            ])
        movies_dataset.drop(["release_date", "video_release_date", "IMDb_URL", "unknown"], axis=1)
        movies_dataset.to_sql('movie', conn, if_exists='fail', index=False)
    except:
        pass


    # RATING DATASET
    try:
        rating_dataset = pd.read_csv("./Dataset/Working/u.data", names=['user_id', 'item_id', 'rating', 'timestamp'], delimiter="\t")
        rating_dataset.to_sql('rating', conn, if_exists='fail', index=False)
    except:
        pass

    conn.commit()

    return conn




@app.route('/') 
def index():
    conn = get_connection()
    return render_template('index.html')



@app.route('/login')
def about():
    conn = get_connection()
    return render_template('login.html', error=False)



@app.route('/genre', methods=['GET', 'POST'])
def execute():
    conn = get_connection()
    cursor = conn.cursor()

    selected_genres = request.form.getlist('genres')
    
    # Call the function to generate recommendations
    recommendations = genre_recommendations(selected_genres)

    genre_string = ','.join(selected_genres).replace(",", ", ")

    # Pass recommendations to the template
    return render_template('genre.html', recommendations=recommendations, selectedGenresString=genre_string)



@app.route('/user', methods=['POST'])
def user():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Retrieving the user ID from the form
        user_id = int(request.form['userId'])

        # GET USER DATA =======================================================================================================
        cursor.execute(f"SELECT * FROM user WHERE user_id = {user_id}")

        # Fetch all rows of the result set
        user_data = cursor.fetchone()
        # =====================================================================================================================

        # GET MOVIE RECOMMENDATIONS ===========================================================================================
        cursor.execute("SELECT * FROM rating")
        ratings_dataset = cursor.fetchall()
        
        cursor.execute("SELECT * FROM movie")
        movie_dataset = cursor.fetchall()
        
        recommendations_dataset = user_recommendations(user_id, ratings_dataset, movie_dataset)
        # =====================================================================================================================

        # GET MOVIES AND THEIR RATING BY USER =================================================================================
        cursor.execute(f"""
            SELECT 
                movie.item_id, 
                movie.title,
                rating.user_id,
                rating.rating
            FROM movie
            LEFT JOIN rating ON movie.item_id = rating.item_id AND rating.user_id = {user_id}
        """)

        movies_dataset = cursor.fetchall()
        # =====================================================================================================================

        # Check if user_data exists in the dataframe
        if user_data:
            return render_template('user.html', user_data=user_data, recommendations=recommendations_dataset, movies=movies_dataset)
        else:
            return render_template('login.html', error=True)
        
    except (Exception, KeyError, ValueError) as e:
        # Handle errors such as missing key in form or inability to convert to integer
        print("Error:", e)
        return render_template('login.html', error=True)



@app.route('/update', methods=['POST'])
def update_rating():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        user_id = int(request.form['user_id'])
        item_id = int(request.form['item_id'])
        rating = int(request.form['rating_value'])


        print("New RATING: ", rating)

        # Check if the record already exists
        cursor.execute("SELECT * FROM rating WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        existing_record = cursor.fetchone()

        # If record exists, update it; otherwise, insert a new record
        if existing_record:
            cursor.execute("UPDATE rating SET rating = ?, timestamp = ? WHERE user_id = ? AND item_id = ?",
                        (rating, int(time.time()), user_id, item_id))
        else:
            cursor.execute("INSERT INTO rating (user_id, item_id, rating, timestamp) VALUES (?, ?, ?, ?)",
                        (user_id, item_id, rating, int(time.time())))

        # Commit changes to the database
        conn.commit()

        print("Database updated successfully.")


        # GET USER DATA =======================================================================================================
        cursor.execute(f"SELECT * FROM user WHERE user_id = {user_id}")

        # Fetch all rows of the result set
        user_data = cursor.fetchone()
        # =====================================================================================================================

        # GET MOVIE RECOMMENDATIONS ===========================================================================================
        cursor.execute("SELECT * FROM rating")
        ratings_dataset = cursor.fetchall()
        
        cursor.execute("SELECT * FROM movie")
        movie_dataset = cursor.fetchall()
        
        recommendations_dataset = user_recommendations(user_id, ratings_dataset, movie_dataset)
        # =====================================================================================================================

        # GET MOVIES AND THEIR RATING BY USER =================================================================================
        cursor.execute(f"""
            SELECT 
                movie.item_id, 
                movie.title,
                rating.user_id,
                rating.rating
            FROM movie
            LEFT JOIN rating ON movie.item_id = rating.item_id AND rating.user_id = {user_id}
        """)

        movies_dataset = cursor.fetchall()
        # =====================================================================================================================

        # Check if user_data exists in the dataframe
        if user_data:
            return render_template('user.html', user_data=user_data, recommendations=recommendations_dataset, movies=movies_dataset)
        else:
            return render_template('login.html', error=True)
    except (Exception, KeyError, ValueError) as e:
        print("Error:", e)
        return render_template('login.html', error=True)



if __name__ == '__main__':
    app.run(debug=True)
