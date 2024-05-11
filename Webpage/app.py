from flask import Flask, request, render_template
from scripts.genreRecommendations import genre_recommendations
from scripts.userRecommendations import user_recommendations, update_u_data
from scripts.movieDataset import get_movies
import sqlite3
import pandas as pd
from flask import g

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
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            occupation TEXT,
            zip_code TEXT
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movie (
            item_id INTEGER PRIMARY KEY,
            title TEXT,
            Action INTEGER,
            Adventure INTEGER,
            Animation INTEGER,
            Childrens INTEGER,
            Comedy INTEGER,
            Crime INTEGER,
            Documentary INTEGER,
            Drama INTEGER,
            Fantasy INTEGER,
            Film_Noir INTEGER,
            Horror INTEGER,
            Musical INTEGER,
            Mystery INTEGER,
            Romance INTEGER,
            Sci_Fi INTEGER,
            Thriller INTEGER,
            War INTEGER,
            Western INTEGER
        )''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating (
            user_id INTEGER,
            item_id INTEGER,
            rating INTEGER,
            timestamp INTEGER,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (item_id) REFERENCES movie(item_id)
        )''')

    conn.commit()

    # USER DATASET
    user_dataset = pd.read_csv("Dataset/Working/u.user", names=['user_id', 'age', 'gender', 'occupation', 'zip_code'], delimiter="|")
    user_dataset.to_sql('user', conn, if_exists='replace', index=False)

    # MOVIE DATASET
    movies_dataset = pd.read_csv("./Dataset/Working/u.item", delimiter="|", encoding="latin1",
                                names=["item id", "title", "release date", 
                                        "video release date", "IMDb URL", "unknown", 
                                        "Action", "Adventure", "Animation",
                                        "Childrens", "Comedy", "Crime",
                                        "Documentary", "Drama", "Fantasy",
                                        "Film-Noir", "Horror", "Musical",
                                        "Mystery", "Romance", "Sci-Fi",
                                        "Thriller", "War", "Western"
                                        ])
    movies_dataset.drop(["release date", "video release date", "IMDb URL", "unknown"], axis=1)
    movies_dataset.to_sql('movie', conn, if_exists='replace', index=False)

    # RATING DATASET
    rating_dataset = pd.read_csv("./Dataset/Working/u.data", names=['user id', 'item id', 'rating', 'timestamp'], delimiter="\t")
    rating_dataset.to_sql('rating', conn, if_exists='replace', index=False)

    return conn




@app.route('/') 
def index():
    conn = get_connection()

    return render_template('index.html')



@app.route('/login')
def about():
    return render_template('login.html', error=False)



@app.route('/genre', methods=['GET', 'POST'])
def execute():
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

        query = f"SELECT * FROM user WHERE user_id = {user_id}"
        user_data = pd.read_sql(query, conn)



        # Check if the record already exists
        cursor.execute("SELECT * FROM rating WHERE user_id = ? AND item_id = ?", (user_id, item_id))

        # Check if user_id exists in the dataframe
        if not user_data.empty:
            return render_template('user.html', user_data=user_data, recommendations=user_recommendations(user_id, conn), movies=get_movies(user_id))
        else:
            return render_template('login.html', error=True)
        
    except (Exception, KeyError, ValueError) as e:
        # Handle errors such as missing key in form or inability to convert to integer
        print("Error:", e)
        return render_template('login.html', error=True)



@app.route('/update', methods=['POST'])
def update_rating():
    try:
        user_id = int(request.form['user_id'])
        item_id = int(request.form['item_id'])
        rating = int(request.form['rating_value'])

        print("New RATING: ", rating)


        # Call your update_rating function here
        update_u_data(user_id, item_id, rating)

        #wait for this to finish

        # Back to page
        #return render_template('user.html', user_data=user_data, recommendations=user_recommendations(user_id), movies=get_movies(user_id))
    except (Exception, KeyError, ValueError) as e:
        print("Error:", e)
        return render_template('login.html', error=True)



if __name__ == '__main__':
    app.run(debug=True)
