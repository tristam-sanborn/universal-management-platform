# Import flask and mySQL Connector
from flask import Flask, request, session, redirect, render_template
import mysql.connector

# Create flask app object
app = Flask(__name__)

# Set secret key
app.secret_key = "create_a_secret_key_before_deployment"

# Create mySQL connection log in with the loginSvgMgr account (has database perms and can check credentials)
conn = mysql.connector.connect(
    host="localhost",
    user="loginSvcMgr",
    password="18ATBeK.9Zjleo\}sS]N2DMQrdc1WI&J-(;X/,yL!vD3T8P$2",
    database="ump_database"
)


# Create a cursor to execute queries
cursor = conn.cursor()

# Route for the home page
@app.route("/")
def home():
    # Check for user login status
    if "username" in session:
        # This will check the users permission level and then load either the admin or user portal accordingly
        print("testprint")
        perm = session["permission"]
        print(perm)
        if session["permission"] == (0,):
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
            session["password"] = password
            #Once we know the user is authenticated add their permission level to their session
            cursor.execute("SELECT permission FROM employees WHERE username = %s AND password = %s", (str(username), str(password)))
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
@app.route('/admin')
def admin():
    userConnection = mysql.connector.connect(
        host="localhost",
        user=session["username"],
        password=session["password"],
        database="ump_database"
    )
    userCursor = userConnection.cursor()
    data = userCursor.execute("SELECT * FROM employees")
    print(data)
    return render_template('admin.html', data=data)

@app.route('/user')
def user():
    return render_template('user.html')

# Run the app on port 5000
if __name__ == "__main__":
    app.run(port=5000)