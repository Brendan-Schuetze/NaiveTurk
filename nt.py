# Import Libraries
from flask import Flask
from flask_pymongo import PyMongo
from time import gmtime, strftime
from werkzeug.routing import BaseConverter
from bson import Binary, Code
from bson.json_util import dumps
from base64 import b64encode
from os import urandom
from flask_bcrypt import Bcrypt

# Start Flask App
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
mongo = PyMongo(app)

# Password Hashing Function
def hashKey(key):
    hash = bcrypt.generate_password_hash(key)
    return hash

# Helper Function for Generating Hashes and Inserting into DB
def createKeySet(public_key, private_key):
    hash = hashKey(private_key)

    existing = mongo.db.keys.find_one({"public_key": public_key})
    if existing is None:
        mongo.db.keys.insert({"public_key": public_key, "hash": hash})
        return("Success.")
    else:
        return("Username already taken.")

# Find Worker
def findWorker(user):
    return(mongo.db.id.find_one({"worker": user}))

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
        private_key_real = requester["hash"]
        return(bcrypt.check_password_hash(private_key_real, private_key_test))
    return(False)

# Create Keyset for Accessing Authenticated Information
@app.route("/create/<public_key>/<private_key>/", methods = ['GET'])
def createUser(public_key, private_key):
    return(createKeySet(public_key, private_key))

# Dump All Information Regarding User
@app.route("/dump/<public_key>/<private_key_test>/<user>/", methods = ['GET'])
def dumpUser(public_key, private_key_test, user):
    user_doc = findWorker(user)

    if user_doc is None:
        return("User Not Found.")
    elif authenticateRequester(public_key, private_key_test):
            return(dumps(user_doc))
    else:
        return("Not Authenticated.")

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET'])
@app.route("/check/<user>/<list:tags>/", methods = ['GET'])
def checkUserStatus(user, tags = "NA"):
    user_doc = mongo.db.id.find_one({"worker": user})

    if user_doc is None:
        return("User Not Found.")
    else:
        id = user_doc["_id"]
        mongo.db.id.update({ "_id" : id}, { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})

        for tag in tags:
            if(tag in user_doc["tags"]):
                return(True)
        return(False)


# Method for Updating Tags Associated with User
@app.route("/add/<public_key>/<private_key_test>/<user>/<list:tags>/", methods = ['POST'])
def updateUserStatus(user):
    if authenticateRequester(public_key, private_key):
        return "Testing"
    else:
        return("Not Authenticated.")

# Homepage
@app.route("/")
def csv():
    return "Welcome to NaiveTurk"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', debug = True)
