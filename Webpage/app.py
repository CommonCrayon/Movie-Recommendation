from flask import Flask, request, render_template

app = Flask(__name__)

# Function to generate movie recommendations based on selected genres
def generate_recommendations(selected_genres):
    # Implement your recommendation generation logic here
    recommendations = ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
    return recommendations

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
