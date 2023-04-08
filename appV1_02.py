# Import flask and mySQL Connector
from flask import Flask, request, session, redirect, render_template, url_for
import mysql.connector

# Create flask app object
app = Flask(__name__)

# Set secret key
app.secret_key = "create_a_secret_key_before_deployment"

# Create mySQL connection log in with the loginSvgMgr account (has database perms and can check credentials)
def getSvcConnection():
    conn = mysql.connector.connect(
    host="localhost",
    user="loginSvcMgr",
    password="18ATBeK.9Zjleo\}sS]N2DMQrdc1WI&J-(;X/,yL!vD3T8P$2",
    database="ump_database"
    )
    return conn
# Create a cursor to execute queries
    

def getConnection():
    userConnection = mysql.connector.connect(
        host='localhost',
        user=session["username"],
        password=session["password"],
        database='ump_database'
    )
    return userConnection
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
            
            return redirect("/users")
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
        conn = getSvcConnection()
        cursor = conn.cursor()
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
            cursor.execute("SELECT uid FROM employees WHERE username = %s AND password = %s", (str(username), str(password)))
            uid = cursor.fetchone()
            session["permission"] = permission
            session["uid"] = uid
            cursor.close()
            conn.close()
            



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
    userConnection = getConnection()
    userCursor = userConnection.cursor()
    userUID = session["uid"]
    
    return render_template('admin.html', data=data)




@app.route('/user')
def user():
    #REDIRECT TO USERS PROFILE PAGE
    return render_template('user.html')




@app.route('/search_results', methods=['POST'])
def search_results():
    # Get the search term from the webpage form
    search_query = request.form['search_query'] 

    # Query the database with user's connection
    searchCnx = getConnection()
    searchCursor = searchCnx.cursor()
    #need to fix lastname and company_name and add back
    searchCursor.execute(f"SELECT uid, username, firstname, lastname, email, role, manager, company_name FROM employees WHERE username LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR email LIKE %s OR role LIKE %s OR manager LIKE %s OR company_name LIKE %s;", (f'%{search_query}%',)*7)
    results = searchCursor.fetchall()

    # Close the database connection
    searchCursor.close()
    searchCnx.close()

    return render_template('search_results.html', results=results)

@app.route('/users')
def users():
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT uid, username FROM employees")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('users.html', users=users)



@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT uid, username, firstname, lastname, email, phone, address, role, manager, company_name FROM employees WHERE uid=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        return "User not found", 404

    return render_template('profile.html', user=user)

@app.route('/profile/<int:user_id>/update', methods=['POST'])
def update_profile(user_id):
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    role = request.form['role']
    manager = request.form['manager']
    company_name = request.form['company_name']

    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees SET
            firstname=%s, lastname=%s, email=%s, phone=%s, address=%s, role=%s, manager=%s, company_name=%s
        WHERE uid=%s
    """, (firstname, lastname, email, phone, address, role, manager, company_name, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('profile', user_id=user_id))



@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        role = request.form['role']
        manager = request.form['manager']
        company_name = request.form['company_name']
        permissionLevel = request.form['permission_level']

        conn = getConnection()
        cursor = conn.cursor()
        if permissionLevel == "admin":
            permission = 0
            cursor.execute("""
            INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name))
        # Insert the new user into the employees table
            cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'")
        
        
        if permissionLevel == "regular_user":
            permission = 1
            cursor.execute("""
            INSERT INTO employees (username, password, firstname, lastname, email, phone, address, role, manager, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name))
            cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'")
        

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('users'))

    return render_template('create_user.html')

@app.route('/delete', methods=['POST'])
def delete_profile(user_id):
    confirmation = request.form['confirmationList']
    passwordRentry = request.form['passwordBox']
    if confirmation == "confirm":
        conn = getConnection()
        cursor = conn.cursor()
        authenticated = (cursor.exectute("SELECT * from employees WHERE username = %s and password = %s", session["username"], passwordRentry))
        if authenticated:
            username = cursor.exectute("SELECT username from employees WHERE uid = %s", user_id)
            cursor.execute("DROP %S", username)

        
    else:
        return redirect(url_for('admin', user_id=user_id))


    return redirect(url_for('admin', user_id=user_id))



def auditHistory(sqlcommand, modifiedUID, modifiedByUID):
    #break down the sql input and add it to to corresponding UID's audit log file
    return
# Run the app on port 5000
if __name__ == "__main__":
    app.run(port=5000)