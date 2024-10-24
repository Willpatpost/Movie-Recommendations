import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename

###### Helper functions #######
def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]

def get_index_from_title(title):
    try:
        return df[df.title.str.lower() == title.lower()]["index"].values[0]
    except IndexError:
        return None  # Return None if the movie title isn't found

# Step 1: Read CSV file
df = pd.read_csv("movie_dataset.csv")

# Step 2: Select Features
features = ['keywords', 'cast', 'genres', 'director']

# Step 3: Create a column in DF that combines all selected features
for feature in features:
    df[feature] = df[feature].fillna('')

def combine_features(row):
    try:
        return row['keywords'] + " " + row['cast'] + " " + row["genres"] + " " + row["director"]
    except Exception as e:
        print(f"Error: {e}")

df["combined_features"] = df.apply(combine_features, axis=1)

# Step 4: Create count matrix from this new combined column
cv = CountVectorizer()
count_matrix = cv.fit_transform(df["combined_features"])

# Step 5: Compute the Cosine Similarity based on the count_matrix
cosine_sim = cosine_similarity(count_matrix)

# Caching to optimize performance
cached_movie_index = None
cached_similar_movies = None

# Function to recommend movies
def recommend_movies():
    global cached_movie_index, cached_similar_movies

    movie_user_likes = movie_entry.get().strip()
    movie_entry.delete(0, tk.END)  # Clear the input field after submission
    movie_index = get_index_from_title(movie_user_likes)

    if movie_index is None:
        # Suggest similar titles if exact title isn't found
        suggestions = [title for title in df['title'] if movie_user_likes.lower() in title.lower()]
        if suggestions:
            messagebox.showinfo("Not Found", f"Did you mean one of these?\n{', '.join(suggestions[:5])}")
        else:
            messagebox.showerror("Error", "Sorry, the movie title was not found in the dataset.")
        return
    
    # Cache the results if the same movie is queried again
    if movie_index == cached_movie_index:
        similar_movies = cached_similar_movies
    else:
        cached_movie_index = movie_index
        similar_movies = list(enumerate(cosine_sim[movie_index]))
        cached_similar_movies = similar_movies
    
    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
    
    # Clear previous results
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Movies similar to '{movie_user_likes}':\n\n")
    
    i = 0
    for element in sorted_similar_movies:
        if element[0] != movie_index:  # Exclude the input movie itself
            result_text.insert(tk.END, f"{get_title_from_index(element[0])} (Score: {element[1]:.2f})\n")
            i += 1
            if i >= 20:
                break

# Function to save results to a text file
def save_results():
    file_path = asksaveasfilename(defaultextension=".txt", 
                                  filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, "w") as file:
            file.write(result_text.get(1.0, tk.END))

# Function to update suggestions as the user types
def update_suggestions(*args):
    typed = movie_entry.get().lower()
    suggestions = [title for title in df['title'] if title.lower().startswith(typed)]
    listbox.delete(0, tk.END)
    for suggestion in suggestions[:10]:  # Limit suggestions to top 10
        listbox.insert(tk.END, suggestion)

# Function to fill the entry with the selected suggestion
def fill_movie_entry(event):
    selected = listbox.get(listbox.curselection())
    movie_entry.delete(0, tk.END)
    movie_entry.insert(0, selected)
    listbox.delete(0, tk.END)

# Step 6: Tkinter GUI for user interaction
app = tk.Tk()
app.title("Movie Recommender")

# Create the input field for movie title
movie_label = tk.Label(app, text="Enter a movie title:", font=("Arial", 14), padx=10, pady=10)
movie_label.pack()

# Create the input field for movie title (Corrected padx and pady usage)
movie_entry = tk.Entry(app, width=50, font=("Arial", 12))
movie_entry.pack(padx=5, pady=5)

# Bind the input field to update suggestions as the user types
movie_entry.bind('<KeyRelease>', update_suggestions)

# Create a Listbox to show the suggestions
listbox = tk.Listbox(app, height=5, font=("Arial", 12))
listbox.pack()

# Bind the listbox to fill the entry with selected suggestion
listbox.bind('<<ListboxSelect>>', fill_movie_entry)

# Create the "Recommend" button
recommend_button = tk.Button(app, text="Recommend", command=recommend_movies, font=("Arial", 12), padx=10, pady=5)
recommend_button.pack()

# Create a frame for the results and scrollbar
result_frame = tk.Frame(app)
result_frame.pack()

# Create a scrollbar
scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create the text area to display the results, link it with the scrollbar
result_text = tk.Text(result_frame, height=20, width=60, font=("Arial", 12), padx=5, pady=5, yscrollcommand=scrollbar.set)
result_text.pack(side=tk.LEFT)

# Configure the scrollbar
scrollbar.config(command=result_text.yview)

# Create the "Save Results" button
save_button = tk.Button(app, text="Save Results", command=save_results, font=("Arial", 12), padx=10, pady=5)
save_button.pack(pady=10)

# Run the Tkinter event loop
app.mainloop()
