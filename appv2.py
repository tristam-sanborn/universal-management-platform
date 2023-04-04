# A Python program that runs a flask server and connects to a mySQL database
from flask import Flask, request, session, redirect, render_template
import mysql.connector

# Create a flask app object
app = Flask(__name__)

# Set a secret key for the session
app.secret_key = "create_a_secret_key_before_deployment"

# Create a mySQL connection object
conn = mysql.connector.connect(
    host="localhost",
    user="loginSvcMgr",
    password="18ATBeK.9Zjleo\}sS]N2DMQrdc1WI&J-(;X/,yL!vD3T8P$2",
    database="ump_database"
)

# Create a cursor object to execute queries
cursor = conn.cursor()

# Define a route for the home page
@app.route("/")
def home():
    # Check if the user is logged in
    if "username" in session:
        # Return a welcome message with the username

        if session["permission"] == 0:
            return redirect("/admin")
        else:
            return redirect("/user")

    
    else:
        # Redirect to the login page
        return redirect("/login")

# Define a route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the request method is POST
    if request.method == "POST":
        # Get the username and password from the form
        username = request.form["username"]
        password = request.form["password"]

        # Query the database to check if the credentials are valid
        cursor.execute("SELECT * FROM employees WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()

        # If the result is not None, the credentials are valid
        if result:
            # Store the username in the session
            session["username"] = username
            cursor.close
            #Once we know the user is authenticated add their permission level to their session
            cursor.execute("SELECT permission FROM employees WHERE username = %s AND password = %s", (username, password))
            permission = cursor.fetchone()
            session["permission"] = permission

            # Redirect to the home page
            return redirect("/")
        else:
            # Return an error message
            return "Invalid username or password"
    else:
        # Return the login template
        return render_template("login.html")

# Define a route for the logout page
@app.route("/logout")
def logout():
    # Remove the username from the session
    session.pop("username", None)

    # Redirect to the login page
    return redirect("/login")

# Run the app on port 5000
if __name__ == "__main__":
    app.run(port=5000)