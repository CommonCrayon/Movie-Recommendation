import pandas as pd


# Reading the dataset
user_dataframe = pd.read_csv("./Dataset/Working/u.data", names=['user id', 'item id', 'rating', 'timestamp'], delimiter="\t")
user_dataframe = user_dataframe.drop(["timestamp"], axis=1)


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


def get_movies(user_id):
    # Filter for the given user id
    filtered_dataframe = user_dataframe[user_dataframe['user id'] == user_id]

    # Merge using left join to keep all movies
    merged_dataframe = movies_dataframe.merge(filtered_dataframe, on='item id', how='left')
    
    print(merged_dataframe)
    return merged_dataframe