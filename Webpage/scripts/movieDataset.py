import pandas as pd

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

def get_movies():
    return movies_dataframe