from flask import Flask, request, render_template
from scripts.genreRecommendations import genre_recommendations
from scripts.userRecommendations import user_recommendations, get_user_data, update_u_data
from scripts.movieDataset import get_movies

app = Flask(__name__)

@app.route('/') 
def index():
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
    try:
        # Retrieving the user ID from the form
        user_id = int(request.form['userId'])

        user_data = get_user_data(user_id)

        # Check if user_id exists in the dataframe
        if not user_data.empty:
            return render_template('user.html', user_data=user_data, recommendations=user_recommendations(user_id), movies=get_movies(user_id))
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

        user_data = get_user_data(user_id)

        # Call your update_rating function here
        update_u_data(user_id, item_id, rating)

        #wait for this to finish

        # Back to page
        return render_template('user.html', user_data=user_data, recommendations=user_recommendations(user_id), movies=get_movies(user_id))
    except (Exception, KeyError, ValueError) as e:
        print("Error:", e)
        return render_template('login.html', error=True)



if __name__ == '__main__':
    app.run(debug=True)
