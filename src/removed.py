@app.route('/login', methods=["GET","POST"])
def login():
    # redirect(url_for('login'))
    if request.method == "POST":
        req = request.form

        username = req["username"]
        password = req["password"]

        # Handle registration faults
        feedbackLogin = ""
        # Check for any missing fields
        missing = list()
        for key, value in req.items():
            if value == "":
                missing.append(key)
        if missing:
            feedbackLogin += f"Missing fields for {', '.join(missing)}. "
            return redirect(request.url)

        # Retrieve salt from database by matching username
        dbcursor.execute("SELECT uid, username, password, salt FROM users WHERE username = %s",(username,))
        rowCount = dbcursor.rowcount
        if rowCount == 0:
            feedbackLogin += f"That username doesn't exist. "
        # Get values into tuple
        result = dbcursor.fetchall()
        # Hash and salt the password
        salt = result[0][3]
        hashedPass = result[0][2]
        passCopy = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
        if passCopy != (hashedPass):
            feedbackLogin += f"Incorrect password. "

        if feedbackLogin != "":
            # Don't login and return feedback
                return redirect(request.url)
        # Start session to login
        session["uid"] = result[0][0]
        session["username"] = result[0][1]
        return redirect(request.url)

    return redirect(request.url)


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        req = request.form

        username = req["username"]
        email = req["email"]
        password = req["password"]
        passcheck = req["passcheck"]

        # Handle registration faults
        feedback = ""
        # Check for any missing fields
        missing = list()
        for key, value in req.items():
            if value == "":
                missing.append(key)
        if missing:
            feedback += f"Missing fields for {', '.join(missing)}. "

        # Maximum length of password is 128 chars
        if len(password) > 128:
            feedback += f"Password should not exceed 128 characters. "
        if len(password) < 8:
            feedback += f"Password should exceed 8 characters."
        if len(username) > 50:
            feedback += f"Username cannot be longer than 50 characters."

        feedback = registerChecks.passwordMatch(password,passcheck,feedback)
        feedback = registerChecks.usernameMatch(username,feedback,dbcursor)
        feedback = registerChecks.emailMatch(email,feedback,dbcursor)
        if feedback != "":
            return render_template("register/index.html", feedback=feedback)

        # Since all checks passed, free to add data to database
        # Hash the password
        # you can replace this with pbkdf2 or scrypt 
        salt = uuid.uuid4().hex
        hashPass = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
        dbcursor.execute("INSERT INTO users (username, email, password, salt) VALUES (%s,%s,%s,%s)",(username,email,hashPass,salt))
        # Add handling if it fails #############
        database.commit()

        # Redirect to login to begin session
        return redirect(request.url)

    return render_template("register/index.html")



<a href="{{ url_for('register') }}"><button>Register</button></a>
<a href="{{ url_for('login') }}"><button>Login</button></a>
<a href="{{ url_for('logout') }}"><button>Logout</button></a>