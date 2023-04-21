# Import flask, mySqlconnector, os, json, datetime, werkzeug.utils
from flask import Flask, request, session, redirect, render_template, url_for, flash, jsonify, send_from_directory
import mysql.connector
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

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
        return redirect("/homepage")

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
        # Return the login page template
        return render_template("login.html")
    


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('homepage'))



#admin has been replaced by users for now, in complete implementation "users" would be moved back to admin
@app.route('/admin')
def admin():
    userConnection = getConnection()
    userCursor = userConnection.cursor()
    userUID = session["uid"]
    
    return render_template('admin.html')



#this page no longer really does anything, just redirects to profile page 
@app.route('/user')
def user():
    #REDIRECT TO USERS PROFILE PAGE
    user_id = session["uid"]
    uid = user_id[0]
    return redirect(url_for('profile', user_id=uid))

#front page for website, doesn't have to do anything just load the template
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

#Where you get re-directed to after clicking on UMP in the company list
@app.route('/ump')
def ump():
    return render_template('login.html')

#this is the page that displays search results, would make more sense to rename to search because it also does the search operation
# originally had a search page where the search was done which is the reason for the name.
@app.route('/search_results', methods=['POST'])
def search_results():
    # Get the search term from the webpage form called search_query
    search_query = request.form['search_query'] 

    # Query the database with user's credentials which means it can only show what they can access
    searchCnx = getConnection()
    searchCursor = searchCnx.cursor()
    #searches by all parameters, possible point to build on could allow users to select what they want to search by
    searchCursor.execute(f"SELECT uid, username, firstname, lastname, email, role, manager, company_name FROM employees WHERE username LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR email LIKE %s OR role LIKE %s OR manager LIKE %s OR company_name LIKE %s;", (f'%{search_query}%',)*7)
    results = searchCursor.fetchall()

    # Close the database connection
    searchCursor.close()
    searchCnx.close()

    return render_template('search_results.html', results=results)


#This is a duplicate of the search function for users just checks a different table, might be good to add asset search to user search and just have one search box
@app.route('/asset_search_results', methods=['POST'])
def asset_search_results():
    # Get the search term from the webpage form
    asset_search_query = request.form['asset_search_query'] 

    # Query the database with user's credentials which means it can only show what they can access
    searchCnx = getConnection()
    searchCursor = searchCnx.cursor()
    #searches assetlist table for asset parameters
    searchCursor.execute(f"SELECT assetid, assetOwner, assetName, location, assetCount FROM assetlist WHERE assetid LIKE %s OR assetOwner LIKE %s OR assetName LIKE %s OR location LIKE %s OR assetCount LIKE %s;", (f'%{asset_search_query}%',)*5)
    results = searchCursor.fetchall()

    # Close the database connection
    searchCursor.close()
    searchCnx.close()

    return render_template('asset_search_results.html', results=results)

#This is the current admin portal homepage
@app.route('/users')
def users():
    conn = getConnection()
    cursor = conn.cursor()
    #query database to get data to put into the employee list on homepage
    cursor.execute("SELECT uid, username FROM employees")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('users.html', users=users)


#page for a users profile page
@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = getConnection()
    cursor = conn.cursor()
    #pull users information from table based off of UID to add to fields on webpage
    cursor.execute("SELECT uid, username, firstname, lastname, email, phone, address, role, manager, company_name FROM employees WHERE uid=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    #404 error if the user get pulled up by UID, should probably make this redirect back to previous page with pop-up warning about no results
    if user is None:
        return "User not found", 404
    
    #Pull up profile picture from storage for the user
    profile_picture_path = os.path.join('static', f'profile_pictures/{user_id}profilepicture.jpg')
    profile_picture_exists = os.path.exists(profile_picture_path)

    return render_template('profile.html', user=user,profile_picture_exists=profile_picture_exists)

#Responsible for making a profile editable through the text boxes on the profile page
@app.route('/profile/<int:user_id>/update', methods=['POST'])
def update_profile(user_id):
    #pull previous values from text boxes so we can update anything that changes
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
    #because we got the form values from before any changes were made we just overwrite everything with the new data and anything that was unchanged stays the same value
    #should probably add some checks to entries in the form before pushing this
    cursor.execute("""
        UPDATE employees SET
            firstname=%s, lastname=%s, email=%s, phone=%s, address=%s, role=%s, manager=%s, company_name=%s
        WHERE uid=%s
    """, (firstname, lastname, email, phone, address, role, manager, company_name, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('profile', user_id=user_id))


#Create user page
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    #If POST then load page and pull values from all fields to add to users profile
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
        #decides admin or user this would be expanded to have more roles in the future
        permissionLevel = request.form['permission_level']

        conn = getConnection()
        cursor = conn.cursor()
        #create admin user this will give them different permissions in the database
        if permissionLevel == "admin":
            #0 for permission in database signifies admin, this should be changed to be mroe obvious
            permission = 0
            #insert into table
            cursor.execute("""
            INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name))
            #commit add to table so that uid gets created
            conn.commit()

            cursor.execute("SELECT uid FROM employees WHERE username = %s and password = %s and firstname = %s and lastname = %s ", (username, password, firstname, lastname))
            newUserUID = cursor.fetchone()
            userFullName = firstname + lastname
            #send to audit_log_query to add the creation statement to the audit log and create their audit log file, the TRUE at the end is to signify that it is a user creation action
            audit_log_query(("INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)), newUserUID, session["uid"], userFullName, True)


            # Insert the new user into the employees table
            audit_log_query(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'", newUserUID, session["uid"], userFullName, False)
            audit_log_query(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'", newUserUID, session["uid"], userFullName, False)
        
        #Create regular user account
        if permissionLevel == "regular_user":
            #permission of 1 signifies regular user
            permission = 1
            #add to table
            cursor.execute("""
            INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name))
            #commit to table
            conn.commit()
            userFullName = firstname + lastname
            cursor.execute("SELECT uid FROM employees WHERE username = %s and password = %s and firstname = %s and lastname = %s ", (username, password, firstname, lastname))
            newUserUID = cursor.fetchone()
            conn.commit()
            audit_log_query(("INSERT INTO employees (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (username, password, permission, firstname, lastname, email, phone, address, role, manager, company_name)), newUserUID, session["uid"], userFullName, True)
            audit_log_query(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'", newUserUID, session["uid"], userFullName,False)
            #These permissions are not correct, we have to decide what we want users to have access to
            audit_log_query(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ump_database.* TO '{username}'@'%'", newUserUID, session["uid"], userFullName, False)

        conn.close()

        return redirect(url_for('users'))

    return render_template('create_user.html')


#Delete user page
#Needs update to use audit_log_query to keep track of deletions
@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_profile(user_id):
    #Drop down list to force a select of delete, and force a password re-entry
    confirmation = request.form['confirmationList']
    passwordRentry = request.form['passwordBox']
    #Check that confirm was selected from drop down
    if confirmation == "confirm":
        conn = getConnection()
        cursor = conn.cursor()
        #Check password with database stored password 
        cursor.execute("SELECT * from employees WHERE username = %s and password = %s", (session["username"], passwordRentry,))
        authenticated = cursor.fetchone()

        if authenticated:
            cursor.execute("SELECT username from employees WHERE uid = %s", (user_id,))
            username = cursor.fetchone()[0]
            uid = get_user_by_id(user_id)
            try:
                #try deleting the user if it fails return the error
                #This was critical to make it so we could delete a user who is just in the table and doesn't have a DB account
                #Would be good to add to audit log for user 
                cursor.execute("DELETE FROM employees WHERE uid = %s", (user_id,))
                cursor.execute("DROP USER %s", (username,))
            except Exception as e:
                print(f"An error occurred while deleting user {username} with ID {user_id}: {e}")
        #if you get your password wrong you get sent to website homepage, no second chances
        else:
            return redirect(url_for('/'))

    else:
        return redirect(url_for('/'))

    #send back to admin portal homepage after deletion complete
    return redirect(url_for('users', user_id=user_id))

#Loads the delete page based off of UID
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


#This function creates our audit log files and tracks all queries sent to the database that are entered through this function 
#Needs update to put audit log files in audit log folder, currently just dumping in running dir
def audit_log_query(query, user_id, modifier_id, userFullName, accountCreation):
    #extract UID from its tuple
    uidNotTuple = user_id[0]
    #Tracking account creation does not play nice with this functions setup because it names the file based off of UID so the creation function is 
    #added after it is run, if you submit a query as accountCreation = TRUE it will only add the query to the audit log file it will not run the query
    if accountCreation == True:
        #opens text file with name scheme UID fullname.txt this should be switched for an encoded filename
        filename = f"{uidNotTuple} {userFullName}.txt"
        with open(filename, 'a') as f:
            f.write(f"Query: {query}\n")
            f.write(f"User ID: {uidNotTuple}\n")
            f.write(f"Modifier ID: {modifier_id}\n")
            f.write("Results: User created\n\n")
        f.close()
    #For anything not accountCreation
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

#modified create_user function
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
        #Need to setup an audit log for assets as well that is where newAssetID would be used as we would have a similar situation to accountCreation
        conn.close()

        return redirect(url_for('assets'))

    return render_template('create_asset.html')

#display asset profile not working currently
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

#should render the about-us.html page, not working
@app.route('/about-us', methods=['POST'])
def aboutus():
    return render_template('about-us.html')

#update asset information the same way user information is updated, would work if asset profile worked
@app.route('/assetprofile/<int:asset_id>/update', methods=['POST'])
def update_asset(asset_id):
    assetName = request.form['asset_name']
    assetCount = request.form['amount_of_asset']
    location = request.form['location']
    assetOwner = request.form['owner_of_asset']

    conn = getConnection()
    cursor = conn.cursor()
    #this should be done in an audit log statement
    cursor.execute("""
        UPDATE employees SET
            assetName=%s, assetCount=%s, location=%s, assetOwner=%s
        WHERE asset_id=%s
    """, (assetName, assetCount, location, assetOwner))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('assetprofile', asset_id=asset_id))

#need to add a delete asset button to asset profile for this to be used currently not configured to work
@app.route('/deleteasset', methods=['POST'])
def delete_asset(asset_id):
    confirmation = request.form['confirmationList']
    passwordRentry = request.form['passwordBox']
    if confirmation == "confirm":
        conn = getConnection()
        cursor = conn.cursor()
        cursor.exectute("SELECT * from employees WHERE username = %s and password = %s", session["username"], passwordRentry)
        authenticated = cursor.fetchone()
        if authenticated:
            username = cursor.exectute("SELECT username from employees WHERE uid = %s", asset_id)
            cursor.execute("DROP %s", username)
            cursor.execute("DELETE FROM `ump_database`.`employees` WHERE (`uid` = %s)", asset_id)        
    else:
        return redirect(url_for('/'))

#same as above
@app.route('/delete_asset/<int:asset_id>', methods=['GET', 'POST'])
def render_asset_delete_page():
    if request.method == 'POST':
        return render_template('delete.html')
    else:
        return redirect(url_for('homepage'))

#setup information for profile pictures to work
current_directory = os.path.dirname(os.path.abspath(__file__))
profile_pictures_folder = os.path.join('static/', 'profile_pictures')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app.config['UPLOAD_FOLDER'] = profile_pictures_folder

# Make sure profile_pictures_folder exists or create it if it doesn't
if not os.path.exists(profile_pictures_folder):
    os.makedirs(profile_pictures_folder)

# check if the uploaded file has a valid extension
def allowed_file(filename):
    #extracts the file extension and checks if it is allowed 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#upload profile picture function
@app.route('/upload_picture/<user_id>', methods=['POST'])
def upload_picture(user_id):
    #if profile picture doesnt exist
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['profile_picture']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(user_id + 'profilepicture.' + file.filename.rsplit('.', 1)[1].lower())
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Add code to update the user's profile picture filename in our database here if we start storing that info in employees table
        return redirect(url_for('profile', user_id=user_id))

    else:
        flash('Invalid file type')
        return redirect(request.url)
    
#Supporting code for the calendar that doesn't work
@app.route('/events.json')
def events_json():
    try:
        with open('events.json', 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        events = []
    return jsonify(events)
#more for the non-functioning calendar
@app.route('/save_events', methods=['POST'])
def save_events():
    #supposed to save created events to events.json
    events = request.get_json()
    with open('events.json', 'w') as f:
        json.dump(events, f)
    return '', 204


# Run the app on port 5000
if __name__ == "__main__":
    app.run(port=5000)