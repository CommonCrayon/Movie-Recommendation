from flask import Flask, request, render_template
import pandas as pd
import sys
from genreRecommendations import genre_recommendations
from userRecommendations import user_recommendations

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
        
        # Load user DataFrame
        user_dataframe = pd.read_csv("../dataset/ml-100k/u.data", names=['userId', 'item id', 'rating', 'timestamp'], delimiter="\t")

        print(user_id, file=sys.stdout)

        # Check if user_id exists in the dataframe
        if user_id in user_dataframe['userId'].values:
            return render_template('user.html', user_id=user_id, recommendations=user_recommendations(user_id))
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

if __name__ == '__main__':
    app.run(debug=True)
