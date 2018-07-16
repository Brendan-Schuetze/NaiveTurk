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
import os
from flask_bcrypt import Bcrypt

# Start Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"

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

# Find Worker
def findWorker(user):
    return(mongo.db.id.find_one({"worker": user}))

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
    if requester is not None:
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

@app.route("/account/", methods = ['GET'])
def accountDetails():
    if not session.get('logged_in'):
        return render_template('account.html')
    else:
        return "Hello Boss!"

@app.route("/login/")
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"

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
    if (methods == "GET" and session.get('logged_in')) or (methods == "POST" and authenticateRequester(request.args.get("username"), request.args.get("password"))):
        user_doc = findWorker(user)

        if user_doc is None:
            return("User Not Found.")
        else:
            return(dumps(user_doc))
    elif methods = "POST":
        return("Not Authenticated.")
    elif methods = "GET":
        return login()

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET'])
@app.route("/check/<user>/<list:tags>/", methods = ['GET'])
def checkUserStatus(user, tags = "NA"):
    user_doc = findWorker(user)

    if user_doc is None:
        return("User Not Found.")
    else:
        id = pingWorker(user_doc)

        for tag in tags:
            if(tag in user_doc["tags"]):
                return("True")
        return("False")


# Method for Updating Tags Associated with User
@app.route("/add/<public_key>/<private_key_test>/<user>/<list:tags>/", methods = ['GET'])
def updateUserStatus(public_key, private_key_test, user, tags):
    if authenticateRequester(public_key, private_key_test):
        user_doc = findWorker(user)
        if user_doc is None:
            return("User Not Found.")
        else:
            id = pingWorker(user_doc)

            for tag in tags:
                if(tag in user_doc["tags"]):
                    mongo.db.id.update({ "_id" : id}, { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})

    else:
        return("Not Authenticated.")

# Homepage
@app.route("/")
def nt():
    return "Welcome to NaiveTurk"

#if __name__ == "__main__":
#    app.run(host ='0.0.0.0', debug = True)

app.secret_key = os.urandom(24)
