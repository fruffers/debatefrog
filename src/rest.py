import dao
from flask import jsonify, request, session
from app import app
from dbconfig import *

@app.route("/loginPoint",methods=["POST"])
def loginPoint():
    _json = request.get_json(force=True)

    _username = _json["username"]
    _password = _json["password"]

    if _username and _password:
        result = dao.loginFunc(_username,_password)

        if "success" in result:
                session["uid"] = result[1]
                session["username"] = result[2]
        
        # set feedback to ajax message feedback
        return jsonify({"message" : "User logged in successfully."})

    return jsonify({"message" : "Bad Request - invalid credentials", "status_code":"400"})

@app.route("/logoutPoint")
def logoutPoint():
    if "uid" in session:
        session.pop("username", None)
        session.pop("uid", None)
        return jsonify({"message" : "You've logged out."})
    return jsonify({"message" : "Bad request."})

@app.route("/regPoint",methods=["POST"])
def regPoint():
    _json = request.get_json(force=True)
    _username = _json["username"]
    _email = _json["email"]
    _password = _json["password"]
    _passcheck = _json["passcheck"]

    result = dao.regFunc(_username,_email,_password,_passcheck)

    if "success" in result:
        session["uid"] = result[1]
        session["username"] = result[2]
        # set feedback to ajax message feedback
        return jsonify({"message" : "Registration successful."})

    return jsonify({"message" : result, "status_code":"400"})

@app.route("/replyPoint",methods=["POST"])
def replyPoint():
    if not session["username"]:
        return jsonify({"message":"Please log in."})
    _json = request.get_json(force=True)
    _title = _json["title"]
    _body = _json["body"]
    _username = session["username"]
    _relate = _json["relate"]
    _claimid = _json["claimid"]

    result = dao.replyFunc(_title,_body,_relate,_username,_claimid)

    if "success" in result:
        return jsonify({"message" : "Successfully posted reply."})

    return jsonify({"message":"There was an error."})

@app.route("/replyreplyPoint",methods=["POST"])
def replyreplyPoint():
    # This makes a reply to a reply so it is important to get the reply id then send 
    # the new reply that is created id back and store in relatedreplies in order for
    # the display and correlation
    if not session["username"]:
        return jsonify({"message":"Please log in."})
    _json = request.get_json(force=True)
    _title = _json["title"]
    _body = _json["body"]
    _username = session["username"]
    _relate = _json["relate"]
    _claimid = _json["claimid"]
    _replyid = _json["replyid"]

    result = dao.replyreplyFunc(_title,_body,_relate,_username,_claimid,_replyid)

    if "success" in result:
        return jsonify({"message" : "Successfully posted reply."})

    return jsonify({"message":"There was an error."})

