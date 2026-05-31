from flask import Flask, request, redirect, render_template_string, session
import sqlite3
import bcrypt

app = Flask(__name__)
app.secret_key = "secretkey"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password BLOB
)
""")

conn.commit()
conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
            return "Registration Successful! <a href='/login'>Login</a>"
        except:
            return "Username already exists!"

    return '''
    <h2>Register</h2>
    <form method="post">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <input type="submit" value="Register">
    </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            session['user'] = username
            return redirect('/dashboard')

        return "Invalid Username or Password"

    return '''
    <h2>Login</h2>
    <form method="post">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"""
        <h2>Welcome, {session['user']}</h2>
        <a href='/logout'>Logout</a>
        """                        
    return redirect('/login')                                  

@app.route('/logout')  
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
