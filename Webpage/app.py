from flask import Flask, request, render_template
from scripts.genreRecommendations import genre_recommendations
from scripts.userRecommendations import user_recommendations, check_user_id
from scripts.movieDataset import get_movies

app = Flask(__name__)

@app.route('/') 
def index():
    return render_template('index.html')



@app.route('/login')
def about():
    return render_template('login.html', error=False)



@app.route('/genre', methods=['POST'])
def execute():
    selected_genres = request.form.getlist('genres')
    print("Selected genres:", selected_genres)
    
    # Call the function to generate recommendations
    recommendations = genre_recommendations(selected_genres)
    
    # Pass recommendations to the template
    return render_template('index.html', recommendations=recommendations)



@app.route('/user', methods=['POST'])
def user():
    try:
        # Retrieving the user ID from the form
        user_id = int(request.form['userId'])

        # Check if user_id exists in the dataframe
        if check_user_id(user_id):
            return render_template('user.html', user_id=user_id, recommendations=user_recommendations(user_id), movies=get_movies(user_id))
        else:
            return render_template('login.html', error=True)
        
    except (KeyError, ValueError) as e:
        # Handle errors such as missing key in form or inability to convert to integer
        print("Error:", e)
        return render_template('login.html', error=True)
    except Exception as e:
        # Handle other unexpected errors
        print("Unexpected Error:", e)
        return render_template('login.html', error=True)



@app.route('/compare', methods=['GET'])
def compare():
    return render_template('compare.html', error=False)


if __name__ == '__main__':
    app.run(debug=True)
