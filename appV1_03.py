# Import flask and mySQL Connector
from flask import Flask, request, session, redirect, render_template, url_for
import mysql.connector
import os
import json
from datetime import datetime

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
    
    return render_template('admin.html')




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
@app.route('/asset_search_results', methods=['POST'])
def asset_search_results():
    # Get the search term from the webpage form
    asset_search_query = request.form['asset_search_query'] 

    # Query the database with user's connection
    searchCnx = getConnection()
    searchCursor = searchCnx.cursor()
    #need to fix lastname and company_name and add back
    searchCursor.execute(f"SELECT assetid, assetOwner, assetName, location, assetCount FROM assetlist WHERE assetid LIKE %s OR assetOwner LIKE %s OR assetName LIKE %s OR location LIKE %s OR assetCount LIKE %s;", (f'%{search_query}%',)*5)
    results = searchCursor.fetchall()

    # Close the database connection
    searchCursor.close()
    searchCnx.close()

    return render_template('asset_search_results.html', results=results)

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
            conn.commit()
            cursor.execute("SELECT uid FROM employees WHERE username = %s and password = %s and firstname = %s and lastname = %s ", (username, password, firstname, lastname))
            newUserUID = cursor.fetchone()
            userFullName = firstname + lastname
            audit_log_query(("INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)), newUserUID, session["uid"], userFullName, True)


        # Insert the new user into the employees table
            audit_log_query(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'", newUserUID, session["uid"], userFullName, False)
            #cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            audit_log_query(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'", newUserUID, session["uid"], userFullName, False)
            #cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'")
                    
        if permissionLevel == "regular_user":
            permission = 1
            cursor.execute("""
            INSERT INTO employees (username, password, firstname, lastname, email, phone, address, role, manager, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name))
            conn.commit()
            userFullName = firstname + lastname
            cursor.execute("SELECT uid FROM employees WHERE username = %s and password = %s and firstname = %s and lastname = %s ", (username, password, firstname, lastname))
            newUserUID = cursor.fetchone()
            conn.commit()
            audit_log_query(("INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)), newUserUID, session["uid"], userFullName, True)
            audit_log_query(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'", newUserUID, session["uid"], userFullName,False)
            #cursor.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            audit_log_query(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'", newUserUID, session["uid"], userFullName)
            #cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'")

        


        conn.close()

        return redirect(url_for('users'))

    return render_template('create_user.html')

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_profile(user_id):
    confirmation = request.form['confirmationList']
    passwordRentry = request.form['passwordBox']
    if confirmation == "confirm":
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT * from employees WHERE username = %s and password = %s", (session["username"], passwordRentry,))
        authenticated = cursor.fetchone()
        if authenticated:
            cursor.execute("SELECT username from employees WHERE uid = %s", (user_id,))
            username = cursor.fetchone()[0]
            uid = get_user_by_id(user_id)
            try:
                cursor.execute("DELETE FROM employees WHERE uid = %s", (user_id,))
                cursor.execute("DROP USER %s", (username,))
            except Exception as e:
                print(f"An error occurred while deleting user {username} with ID {user_id}: {e}")


        
    else:
        return redirect(url_for('/'))


    return redirect(url_for('users', user_id=user_id))
@app.route('/delete_profile/<int:user_id>', methods=['GET', 'POST'])
def render_delete_page(user_id):
    if request.method == 'POST':
        return render_template('delete.html', user_id=user_id)
    else:
        return redirect(url_for('profile'))
    
def get_user_by_id(user_id):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE uid = %s", (user_id,)) # Add a comma to make it a tuple
    user = cursor.fetchone()
    cursor.close()
    return user

def audit_log_query(query, user_id, modifier_id, userFullName, accountCreation):
    # Connect to the MySQL database
    uidNotTuple = user_id[0]
    if accountCreation == True:
        filename = f"{uidNotTuple} {userFullName}.txt"
        with open(filename, 'a') as f:
            f.write(f"Query: {query}\n")
            f.write(f"User ID: {uidNotTuple}\n")
            f.write(f"Modifier ID: {modifier_id}\n")
            f.write("Results: User created\n\n")
        f.close()
    else:
        conn = getConnection()
        cursor = conn.cursor()

        # Execute the query and fetch the results
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()

        # Write the results to a file with the user ID as the filename
        filename = f"{uidNotTuple} {userFullName}.txt"
        with open(filename, 'a') as f:
            f.write(f"Query: {query}\n")
            f.write(f"User ID: {uidNotTuple}\n")
            f.write(f"Modifier ID: {modifier_id}\n")
            f.write("Results:\n")
            for result in results:
                f.write(str(result) + "\n")
            f.write("\n")

    # Close the database connection
        cursor.close()
        conn.close()




#ASSET CODE STARTS HERE:


@app.route('/create_asset', methods=['GET', 'POST'])
def create_asset():
    if request.method == 'POST':
        assetName = request.form['asset_name']
        assetCount = request.form['amount_of_asset']
        location = request.form['location']
        assetOwner = request.form['owner_of_asset']

        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assetlist (assetName, assetCount, location, assetOwner)
            VALUES (%s, %s, %s, %s)
            """, (assetName, assetCount, location, assetOwner))
        conn.commit()
        #If a user has 2 assets with matching names assigned to them this statement will probably break:
        cursor.execute("SELECT assetID FROM assetlist WHERE assetName = %s and assetOwner = %s", (assetName, assetOwner))
        newAssetID = cursor.fetchone()
        #audit_log_query(("INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)), newUserUID, session["uid"], userFullName, True)


        conn.close()

        return redirect(url_for('assets'))

    return render_template('create_asset.html')

@app.route('/assetprofile/<int:asset_id>')
def assetProfile(asset_id):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT assetName, assetCount, location, assetOwner FROM assetlist WHERE assetid=%s", (asset_id,))
    asset = cursor.fetchone()
    cursor.close()
    conn.close()

    if asset is None:
        return "Asset not found", 404

    return render_template('assetprofile.html', asset_id=asset_id)

@app.route('/assetprofile/<int:asset_id>/update', methods=['POST'])
def update_asset(asset_id):
    assetName = request.form['asset_name']
    assetCount = request.form['amount_of_asset']
    location = request.form['location']
    assetOwner = request.form['owner_of_asset']

    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees SET
            assetName=%s, assetCount=%s, location=%s, assetOwner=%s
        WHERE asset_id=%s
    """, (assetName, assetCount, location, assetOwner))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('assetprofile', asset_id=asset_id))

@app.route('/deleteasset', methods=['POST'])
def delete_asset(assetid):
    confirmation = request.form['confirmationList']
    passwordRentry = request.form['passwordBox']
    if confirmation == "confirm":
        conn = getConnection()
        cursor = conn.cursor()
        cursor.exectute("SELECT * from employees WHERE username = %s and password = %s", session["username"], passwordRentry)
        authenticated = cursor.fetchone()
        if authenticated:
            username = cursor.exectute("SELECT username from employees WHERE uid = %s", assetid)
            cursor.execute("DROP %s", username)
            cursor.execute("DELETE FROM `ump_database`.`employees` WHERE (`uid` = %s)", assetid)

        
    else:
        return redirect(url_for('/'))





CALENDAR_FILE = 'calendar.json'

def load_calendar():
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_calendar(calendar_data):
    with open(CALENDAR_FILE, 'w') as f:
        json.dump(calendar_data, f)
@app.route('/addevent', methods=['POST'])   
def add_event(date, event):
    calendar_data = load_calendar()
    if date not in calendar_data:
        calendar_data[date] = []
    calendar_data[date].append(event)
    save_calendar(calendar_data)

@app.route('/calendar', methods=['GET', 'POST'])
def calendar_page():
    if request.method == 'POST':
        date = request.form.get('date')
        event = request.form.get('event')
        add_event(date, event)
        return redirect(url_for('calendar_page'))

    calendar_data = load_calendar()
    return render_template('calendar.html', calendar=calendar_data)


# Run the app on port 5000
if __name__ == "__main__":
    app.run(port=5000)