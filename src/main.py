from flask import Flask, url_for, request, redirect, render_template, session
import mysql.connector
import hashlib, uuid
import os
from datetime import datetime

from rest import *
from app import app
from dbconfig import *
import helpers.registerChecks as registerChecks

@app.route('/')
def main():
    return redirect("/forum")

@app.route('/home')
def welcome():
        if 'username' in session:
            username = session['username']
            feedback = '<p>Logged in as ' + username + '</p>' + "<b><a href = '/logout'>click here to log out</a></b>"
        else:
            feedback = "<p>You are not logged in</p><a href = '/login'>" + "click here to log in</a>"
        return render_template("welcome/index.html",feedback=feedback)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('uid', None)
    return redirect(url_for('main'))

@app.route('/forum', methods=["GET","POST"])
def forum():
    if 'username' in session:
        username = session['username']
    else:
        username = "<b><a style='color:blue;'>" + "please log in</a></b>"

    dbcursor.execute("SELECT title,description FROM topics")
    result = dbcursor.fetchall()
    # Load them
    topics = []
    for (title,desc) in result:
        post = {"name":title,"description":desc}
        topics.append(post)
    
    return render_template("forum/index.html", topics=topics,username=username)

@app.route('/makeClaim', methods=['GET','POST'])
def makeClaim():
    if request.method == "POST":
        req = request.form

        # Handle registration faults
        feedback = ""
        # Check for any missing fields
        missing = list()
        for key, value in req.items():
            if value == "":
                missing.append(key)
        if missing:
            feedback += f"Missing fields for {', '.join(missing)}. "
            return feedback

        title = req["title"]
        relate = req["relate"]
        body = req["body"]
        topic = req["topic"]
        # get username and details also
        uid = session["uid"]
        author = session["username"]
        pdate = datetime.now()

        dbcursor.execute("INSERT INTO claims (title,content,claimrelate,uid,author,topic,dateposted,interactiondate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(title,body,relate,uid,author,topic,pdate,pdate))
        database.commit()
        feedback = "Posted claim successfully."
        # get claims
        return feedback

@app.route('/makeTopic', methods=['GET','POST'])
def makeTopic():
    if request.method == "POST":
        req = request.form

        # Handle registration faults
        feedback = ""
        # Check for any missing fields
        missing = list()
        for key, value in req.items():
            if value == "":
                missing.append(key)
        if missing:
            feedback += f"Missing fields for {', '.join(missing)}. "
            return feedback

        title = req["title"]
        desc = req["body"]
        uid = session["uid"]

        dbcursor.execute("INSERT INTO topics (title,description,uid) VALUES (%s,%s,%s)",(title,desc,uid))
        database.commit()
        feedback = "Posted topic successfully."
        # get claims
        return feedback

@app.route('/forum/<topic>', methods=['GET','POST'])
def topicPage(topic):

    claimtags = [
        "For",
        "Against",
        "Neutral"
    ]

    # Get claims from database, have to make sure to only select claims for relevant topic
    dbcursor.execute("SELECT claimid, title,content,tag,author,rating,topic,interactiondate,dateposted FROM claims WHERE topic = (%s)",(topic,))
    result = dbcursor.fetchall()
    # Load them
    claims = []
    for (pid,ptitle,pcontent,ptag,pauthor,prating,ptopic,pidate,pdate) in result:
        post = {"pid":pid,"ptitle":ptitle,"pbody":pcontent,"ptag":ptag,"pauthor":pauthor,"prating":prating,"ptopic":ptopic,"pidate":pidate,"pdate":pdate}
        claims.append(post)

    # Order claims by interaction date
    claims = sorted(claims, key=lambda k: k["pidate"])

    if 'username' in session:
        username = session['username']
        feedback = ""
    else:
        feedback = "<p>You are not logged in</p><a href = '/login'>" + "click here to log in</a>"

    return render_template('topic/index.html',topic=topic,claimtags=claimtags,claims=claims,feedback=feedback)

@app.route('/forum/<topic>/<claim>/<claimid>', methods=['GET','POST'])
def claimPage(topic,claim,claimid):

    # Get claims from database, have to make sure to only select claims for relevant topic
    dbcursor.execute("SELECT title,content,author,dateposted,claimrelate FROM claims WHERE claimid = (%s)",(claimid,))
    result = dbcursor.fetchall()
    # Load them
    claims = []
    replies = []
    for (title,content,author,dateposted,claimrelate) in result:
        post = {"title":title,"content":content,"author":author,"dateposted":dateposted,"claimrelate":claimrelate}
        claims.append(post)

    if 'username' in session:
        username = session['username']
        feedback = ""
    else:
        feedback = "<p>You are not logged in</p>"

    # Get replies from database
    dbcursor.execute("SELECT title, content, username, replyrelate, claimrelate, replyid FROM replies WHERE claimid = (%s)",(claimid,))
    repliesresult = dbcursor.fetchall()
    for (title,content,username,replyrelate,claimrelate,replyid) in repliesresult:
        reply = {"title":title,"content":content,"username":username,"replyrelate":replyrelate,"claimrelate":claimrelate,"replyid":replyid}
        replies.append(reply)

    commentari = commentaria(4)

    # Get related replies information
    dbcursor.execute("SELECT idrelatedreplies, replyid1, replyid2 FROM relatedreplies WHERE claimid = (%s)",(claimid,))
    relatedrepliesresult = dbcursor.fetchall()
    relatedreplies = []
    for (idrelatedreplies,replyid1,replyid2) in relatedrepliesresult:
        relatedreply = {"idrelatedreplies":idrelatedreplies,"replyid1":replyid1,"replyid2":replyid2}
        relatedreplies.append(relatedreply)

    return render_template('claim/index.html',topic=topic,claims=claims,replies=replies,feedback=feedback,claimid=claimid,relatedreplies=relatedreplies,commentari=commentari)

def commentaria(claimid):
    dbcursor.execute("SELECT replyid FROM replies WHERE claimid = (%s)",(claimid,))
    repliesa = dbcursor.fetchall()
    replies = []
    for i in repliesa:
        rreps = getRepliesToReply(i[0])
        replies.append([i[0],rreps])

    commenti = []
    for count, i in enumerate(replies):
        # Get reply data
        dbcursor.execute("SELECT * FROM replies WHERE replyid = (%s)",(i[0],))
        result = dbcursor.fetchall()
        commenti.append([result[0],[]])
        for j in i[1]:
            # Get replies data
            dbcursor.execute("SELECT * FROM replies WHERE replyid = (%s)",(j,))
            a = dbcursor.fetchall()
            commenti[count][1].append(a[0])

    print("replies..........! ", commenti)
    return replies

def getRepliesToReply(replyid):
    # Get all replies to a reply passed in as parameter
    # These can then be displayed via flask for loop
    dbcursor.execute("SELECT replyid2 FROM relatedreplies WHERE replyid1 = (%s)",(replyid,)) 
    repliesids = dbcursor.fetchall()
    replies = [i[0] for i in repliesids]
    # for i in repliesids:
    #     val = i[0][0]
    #     dbcursor.execute("SELECT * FROM replies WHERE replyid = (%s)",(val,))
    #     reply = dbcursor.fetchall()
    #     replies.append(reply[0][0])

    return replies
    


@app.route('/profile/<username>')
def profileShow(username):
    return 'Hello there!'


if __name__ == "__main__":
    app.run()