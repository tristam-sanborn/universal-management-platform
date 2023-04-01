from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from pydal import DAL


app = Flask(__name__)
app.secret_key = 'secret'  # Create a key for our actual implementation

# Configuring Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
import mysql.connector



class sqlConnect():




    def startConnection():
        db = DAL("mysql://root:password@127.0.0.1:3306/ump_database")
        query = db.executesql("SELECT * FROM employees")
        print(query)
#        cnx = mysql.connector.connect(user='root', password='password',
#                              host='127.0.0.1',
#                              database='ump_database')
#        cursor = cnx.cursor()
#        query = ("SELECT uid FROM employees")
#        cursor.execute(query)
#        for (uid) in cursor:
#            print("uid list:", uid)
#        print("failed if only output is this")
    def endConnection():
        print()
        


# Define the user 
class User(UserMixin):
    def __init__(self, id, name, email, password, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.is_admin = is_admin

# User credential dictionary this will be a database in the future
userList = {
    'admin': User(id='admin', name='admin lastname', email='admin@ump.com', password='password', is_admin=True),
    'user': User(id='user', name='user lastname', email='user@ump.com', password='password', is_admin=False),
    'tristam': User(id='tristam', name='Tristam S', email='tristam@ump.com', password='123', is_admin=True),
    'john': User(id='john', name='John K', email='john@ump.com', password='password', is_admin=True),
    'connor': User(id='connor', name='Connor A', email='connor@ump.com', password='password', is_admin=True),
    'juan': User(id='juan', name='Juan M', email='juan@ump.com', password='password', is_admin=True),
}

# Define user loader
@login_manager.user_loader
def load_user(user_id):
    return userList.get(user_id)

# Defines login view
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in userList:
            user = userList[username]
            if password == user.password:
                login_user(user)
                print (user)
                username = user
                userPassword = user.password
                sqlConnect.startConnection()
                return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

# Defines the home view
@app.route('/')
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('profile'))
        else:
            return render_template('user.html', user=current_user, users=userList)
    else:
        return render_template('index.html')
    
@app.route('/admin')
def admin():
    users = [user for user in userList.values()]
    return render_template('admin.html', users=users)

# Defines the logout view
@app.route('/logout')
@login_required
def logout():
    logout_user()
    sqlConnect.endConnection()    
    return redirect(url_for('login'))

# Defines the profile view
@app.route('/profile')
def profile():
    if current_user.is_admin:
        #Pass in the user who's profile it is here somehow
        return render_template('profile.html', users=userList) 
    else:
        return redirect(url_for('home'))

# Handle unauthorized access
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)