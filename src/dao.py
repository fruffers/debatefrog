import hashlib
from dbconfig import *
import helpers.registerChecks as registerChecks
import uuid

"""
    This Data Access Object fetches information from the database and returns JSON validation.
"""

def loginFunc(username, password):

    # Handle registration faults
    feedbackLogin = ""

    # Retrieve salt from database by matching username
    dbcursor.execute("SELECT uid, username, password, salt FROM users WHERE username = %s",(username,))
    rowCount = dbcursor.rowcount
    if rowCount == 0:
        feedbackLogin += f"That username doesn't exist. "
        return feedbackLogin
    # Get values into tuple
    result = dbcursor.fetchall()
    # Hash and salt the password
    salt = result[0][3]
    hashedPass = result[0][2]
    passCopy = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
    if passCopy != (hashedPass):
        feedbackLogin += f"An error occurred."

    if feedbackLogin != "":
        # Don't login and return feedback
        return feedbackLogin

    # Start session to login and commit to database
    return ["success",result[0][0],result[0][1]]

def regFunc(username, email, password, passcheck):

    # Handle registration faults
    feedback = ""

    # Maximum length of password is 128 chars
    if len(password) > 128:
        feedback += f"Password should not exceed 128 characters. "
    if len(password) < 8:
        feedback += f"Password should exceed 8 characters. "
    if len(username) > 50:
        feedback += f"Username cannot be longer than 50 characters."

    feedback = registerChecks.passwordMatch(password,passcheck,feedback)
    feedback = registerChecks.usernameMatch(username,feedback,dbcursor)
    feedback = registerChecks.emailMatch(email,feedback,dbcursor)
    if feedback != "":
        return feedback

    # Since all checks passed, free to add data to database
    # Hash the password
    # you can replace this with pbkdf2 or scrypt 
    salt = uuid.uuid4().hex
    hashPass = hashlib.sha512((salt+password).encode('utf-8')).hexdigest()
    dbcursor.execute("INSERT INTO users (username, email, password, salt) VALUES (%s,%s,%s,%s)",(username,email,hashPass,salt))
    database.commit()
    return ["success",result[0],result[1]]

def replyFunc(title,body,relate,username,claimid):
    feedback = ""
    #claimchoices = ["clarification","supporting arguement","counter arguement"]
    replychoices = ["evidence","support","rebuttal"]
    if relate in replychoices:
        dbcursor.execute("INSERT INTO replies (title,content,replyrelate,claimid,username) VALUES (%s,%s,%s,%s,%s)",(title,body,relate,claimid,username))
        
    else:
        dbcursor.execute("INSERT INTO replies (title,content,claimrelate,claimid,username) VALUES (%s,%s,%s,%s,%s)",(title,body,relate,claimid,username))
    database.commit()
    feedback = "success"
    return feedback

def replyreplyFunc(title,body,relate,username,claimid,replyid):
    feedback = ""
    #claimchoices = ["clarification","supporting arguement","counter arguement"]
    # Make new reply
    replychoices = ["evidence","support","rebuttal"]
    if relate in replychoices:
        dbcursor.execute("INSERT INTO replies (title,content,replyrelate,claimid,username) VALUES (%s,%s,%s,%s,%s)",(title,body,"reply",claimid,username))
        
    else:
        dbcursor.execute("INSERT INTO replies (title,content,claimrelate,claimid,username) VALUES (%s,%s,%s,%s,%s)",(title,"claim",relate,claimid,username))
    database.commit()
    # Get the generated id... this is not a very good method because there could be duplicate posts
    dbcursor.execute("SELECT LAST_INSERT_ID()")
    replyid2 = dbcursor.fetchall()[0][0]
    dbcursor.execute("INSERT INTO relatedreplies (replyid1, replyid2, claimid) VALUES (%s,%s,%s)",(replyid,replyid2,claimid))
    database.commit()
    # Insert relation into relatedreplies
    feedback = "success"
    return feedback
