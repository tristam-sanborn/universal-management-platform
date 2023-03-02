from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = 'secret'  # Create a key for our actual implementation

# Configuring Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define the user model
class User(UserMixin):
    def __init__(self, username, name, email, password, is_admin=False):
        self.id = username
        self.name = name
        self.email = email
        self.password = password
        self.is_admin = is_admin

# User credentials
userList = {
    'admin': User('admin', 'admin', 'admin@ump.com', 'password', True),
    'user': User('user', 'admin', 'user@ump.com', 'password', False),
}

# Define user loader
@login_manager.user_loader
def load_user(user_id):
    return userList.get(user_id)

# Define login view
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
                return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

# Define the home view
@app.route('/')
@login_required
def home():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin'))
        else:
            return render_template('user.html', user=current_user, users=userList)
    else:
        return render_template('index.html')
    
@app.route('/admin')
def admin():
    users = userList
    return render_template('admin.html', users=userList)

    #return f'Welcome, {current_user.id}!'

# Define the logout view
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Handle unauthorized access
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)