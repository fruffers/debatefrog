def passwordMatch(password,passcheck,feedback):
    # Check if password and passcheck are the same
    if password != passcheck:
        feedback += f"The passwords you entered are not the same. "
    return feedback

def usernameMatch(username,feedback,dbcursor):
    # Check if username or email is taken    
    dbcursor.execute("SELECT username FROM users WHERE username = %s",(username,))
    rowCount = dbcursor.rowcount
    if rowCount != 0:
        feedback += f"That username already exists. "  
    return feedback

def emailMatch(email,feedback,dbcursor):
    dbcursor.execute("SELECT email FROM users WHERE email = %s",(email,))
    rowCount = dbcursor.rowcount
    if rowCount != 0:
        feedback += f"That email already exists. "
    return feedback
