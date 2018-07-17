# Import Libraries
from flask import Flask
from flask import session, redirect, render_template, request, abort
from flask_pymongo import PyMongo
from time import gmtime, strftime
from werkzeug.routing import BaseConverter

# Password Hashign Libraries
from bson import Binary, Code
from bson.json_util import dumps
from base64 import b64encode
from flask_bcrypt import Bcrypt
import os
import hashlib

# Start Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
app.secret_key = os.urandom(24)

# Access Database and Encryption Functions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Password Hashing Function
def hashKey(key):
    hash = bcrypt.generate_password_hash(key)
    return(hash)

# Helper Function for Generating Hashes and Inserting into DB
def createKeySet(public_key, private_key, first_name, last_name, email_address):
    hash = hashKey(private_key)

    existing = mongo.db.keys.find_one({"public_key": public_key})
    existing_email = mongo.db.keys.find_one({"email_address": email_address})
    if existing is not None or existing_email is not None:
        return("Username or email is already taken.")
    else:
        mongo.db.keys.insert({"public_key": public_key, "hash": hash,
            "registered_on": strftime("%Y-%m-%d %H:%M:%S",
            gmtime()), "verified": "False",
            "first_name": first_name, "last_name": last_name,
            "email_address": email_address})
        return("Success.")

def digest(user):
    user = hashlib.sha256(user + "nvt.science").hexdigest()
    return(user)

# Find Worker
def findWorker(user):
    return(mongo.db.id.find_one({"worker": digest(user)}))

# Ping Worker
def pingWorker(user_doc):
    id = user_doc["_id"]
    mongo.db.id.update({ "_id" : id}, { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})
    return(id)

# Update Worker Tags
def pingTag(id, tag):
    return(True)

# List Converter for Converting Tags to a List
class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['list'] = ListConverter

# Authentication Function
def authenticateRequester(public_key, private_key_test):
    requester = mongo.db.keys.find_one({"public_key": public_key})
    if requester is not None and requester["verified"] is not None:
        if requester["verified"] != "True":
            return(False)
        else:
            private_key_real = requester["hash"]
            return(bcrypt.check_password_hash(private_key_real, private_key_test))
    return(False)


# Create Keyset for Accessing Authenticated Information
@app.route("/create/", methods = ['POST'])
def createUser():
    if createKeySet(request.form['username'], request.form['password'], request.form['first_name'], request.form['last_name'], request.form['email_address']) == "Success.":
        return login()
    else:
        return("Failed to create account.")

# Account Creation Page
@app.route("/account/", methods = ['GET'])
def accountDetails():
    if not session.get('logged_in'):
        return render_template('account.html')
    else:
        return nt()

# Login Page
@app.route("/login/")
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return nt()

# Method for Authenticating Username + Password Combo
@app.route("/authenticate/", methods = ['POST'])
def authenticate():
    if authenticateRequester(request.form['username'], request.form['password']):
        session['logged_in'] = True
    else:
        return("Not Authenticated.")
    return nt()

# Dump All Information Regarding User (Admin Functionality)
@app.route("/dump/<user>/", methods = ['GET', 'POST'])
def dumpUser(user):
    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and authenticateRequester(request.form["username"], request.form["password"])):
        user_doc = findWorker(user)

        if user_doc is None:
            return("User Not Found.")
        else:
            return(dumps(user_doc))
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return login()

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET'])
@app.route("/check/<user>/<list:tags>/", methods = ['GET', 'POST'])
def checkUserStatus(user, tags = "NA"):
    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and authenticateRequester(request.form["username"], request.form["password"])):
        user_doc = findWorker(user)
        id = pingWorker(user_doc)

        if user_doc is None:
            return("False")
        else:
            if len(tags) > 0:
                for tag in tags:
                    tag_search = mongo.db.id.find_one({ "_id" : id}, { "tags": {"$eleMatch": {"tag_name": tag}}})

                    if(tag_search is not None):
                        return("True")
                    else:
                        tag_search = None

                return("False")
            return("True")
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return login()


# Method for Updating Tags Associated with User
@app.route("/add/<user>/<list:tags>/", methods = ['GET', 'POST'])
def updateUserStatus(user, tags):
    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and authenticateRequester(request.form["username"], request.form["password"])):
        user_doc = findWorker(user)
        if user_doc is None:
            mongo.db.id.insert({"worker": digest(user),
                "time": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                "pings": [],
                "tags": []})

            id = pingWorker(findWorker(user))

            for tag in tags:
                mongo.db.id.update({ "_id" : id}, { "$push": { "tags": {"tag_name": tag, "tag_time": strftime("%Y-%m-%d %H:%M:%S", gmtime())}}})
        else:
            id = pingWorker(user_doc)

            for tag in tags:
                mongo.db.id.update({ "_id" : id}, { "$push": { "tags": {"tag_name": tag, "tag_time": strftime("%Y-%m-%d %H:%M:%S", gmtime())}}})
        return("Success.")
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return login()

# Homepage
@app.route("/")
def nt():
    return "Welcome to nvt.science"

#if __name__ == "__main__":
#    app.run(host ='0.0.0.0', debug = True)
