# app.py
from flask import Flask, request, render_template, redirect, url_for
from flask import session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

# Connect to MongoDB
client = MongoClient("mongodb+srv://user:user123@cluster0.z5xjddp.mongodb.net/")

# Access the database and collection containing the job data
db = client["database"]
job_data_collection = db["job_data_test"]

# Convert the MongoDB collection into a pandas DataFrame
job_data = pd.DataFrame(list(job_data_collection.find()))

# Vectorize job descriptions
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(job_data["description"])

# Access the database and collection containing the user data
users_collection = db["users"]

# Convert the MongoDB collection into a pandas DataFrame
users = pd.DataFrame(list(users_collection.find()))


# Function to check if the provided username and password are valid

@app.route("/logout")
def logout():
    # Clear the session variable to log out the user
    session.pop("username", None)
    return redirect(url_for("login"))

# Connect to MongoDB
client = MongoClient("mongodb+srv://user:user123@cluster0.z5xjddp.mongodb.net/")
db = client["database"]
users_collection = db["users"]

def verify_login(username, password):
    user = users_collection.find_one({"username": username})
    if user and user['password'] == password:
        return True
    return False


# Decorator function to check if the user is logged in
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            # If user is not logged in, redirect to the login page
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

# ... rest of the code

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        secret_question = request.form["secret_question"]
        
        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            error_message = "Username already exists. Please choose a different one."
            return render_template("signup.html", error_message=error_message)
        
        # Insert the user details into the MongoDB collection with hashed password
        users_collection.insert_one({
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "secret_question": secret_question
        })
        
        # Redirect to login page after successful signup
        return redirect(url_for("login"))
# Add this route to app.py

@app.route("/reset_password", methods=["GET","POST"])
def reset_password():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]
        
        # Update the user's password in the database
        result = users_collection.update_one(
            {"username": username},
            {"$set": {"password": new_password}}
        )
        
        if result.modified_count > 0:
            # Password updated successfully, redirect to login page
            return redirect(url_for("login"))
        else:
            # Failed to update password, display an error message
            error_message = "Failed to reset password. Please try again."
            return render_template("reset_password.html", error_message=error_message)
        
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_login(username, password):
            # Authentication successful, set session variable and redirect to index
            session['username'] = username
            return redirect(url_for("index"))
        else:
            # Authentication failed, show error message
            error_message = "Invalid username or password"
            return render_template("login.html", error_message=error_message)
    return render_template("login.html")

# Add this route to app.py
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        secret_question = request.form["secret_question"]
        
        # Retrieve the user details based on the provided username
        user = users_collection.find_one({"username": username})
        
        if user:
            # Verify if the provided secret question matches the one in the database
            if user["secret_question"] == secret_question:
                # Secret question matches, render a page to reset the password
                return render_template("reset_password.html", username=username)
            else:
                # Secret question doesn't match, display an error message
                error_message = "Secret question does not match."
                return render_template("forgot_password.html", error_message=error_message)
        else:
            # User not found, display an error message
            error_message = "User not found."
            return render_template("forgot_password.html", error_message=error_message)
    
    # Render the forgot password form
    return render_template("forgot_password.html")


@app.route("/recommend", methods=["POST"])
def recommend_skills_and_courses():
    job_title = request.form["job_title"]

    # Find job descriptions matching the provided job title
    matching_jobs = job_data[job_data["title"].str.contains(job_title, case=False)]

    if len(matching_jobs) == 0:
        return render_template("no_results.html", job_title=job_title)

    # Vectorize job descriptions
    job_descriptions = matching_jobs["description"]
    job_tfidf = tfidf_vectorizer.transform(job_descriptions)

    # Calculate cosine similarity between user input and job descriptions
    similarity_scores = cosine_similarity(job_tfidf, tfidf_matrix)

    # Get top matching job
    top_index = similarity_scores.argmax()
    top_job = job_data.iloc[top_index]

    # Extract recommended skills and courses from top job description
    recommended_skills = top_job["skills"].split(", ") if "skills" in top_job else []
    recommended_courses = top_job["courses"].split(", ") if "courses" in top_job else []
    course_links = top_job["course_links"].split(", ") if "course_links" in top_job else []

    # Fetch thumbnails for each course link
    course_thumbnails = []
    for link in course_links:
        thumbnail_url = fetch_thumbnail_url(link)
        if thumbnail_url:
            course_thumbnails.append(thumbnail_url)
        else:
            # Provide a default thumbnail URL in case fetching fails
            course_thumbnails.append("default_thumbnail_url.jpg")

    # Zip recommended courses, links, and thumbnails together
    course_data = zip(recommended_courses, course_links, course_thumbnails)

    return render_template("results.html", job_title=top_job["title"], skills=recommended_skills, courses_with_links=course_data)



def fetch_thumbnail_url(course_link):
    try:
        response = requests.get(course_link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Example: find the <meta> tag containing the thumbnail URL
            thumbnail_meta_tag = soup.find("meta", property="og:image")
            if thumbnail_meta_tag:
                return thumbnail_meta_tag["content"]
    except Exception as e:
        print(f"Error fetching thumbnail for course link {course_link}: {str(e)}")
    return None
@app.route("/")
def ind():
    return redirect(url_for('login'))

@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Protected route - profile page
@app.route("/profile", methods=["GET"])
@login_required
def profile():
    # Get the current user's information from the MongoDB collection
    user = users_collection.find_one({"username": session["username"]})
    return render_template("profile.html", user=user)

@app.route("/about",methods=["GET","POST"])
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")
# ... rest of the code


if __name__ == "__main__":
    app.run(debug=True)
