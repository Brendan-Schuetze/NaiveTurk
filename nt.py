# Import Libraries
from flask import Flask
from flask_pymongo import PyMongo
from time import gmtime, strftime
from werkzeug.routing import BaseConverter
from bson import Binary, Code
from bson.json_util import dumps
from base64 import b64encode
from os import urandom
import bcrypt

# Start Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
mongo = PyMongo(app)

# Password Hashing Functions
def generateSalt():
    bytes = urandom(64)
    salt = b64encode(bytes).decode('utf-8')
    return salt

def hashKey(key, salt):
    hash = bcrypt.hashpw(key, salt)
    return hash

# Helper Function for Generating Hashes and Inserting into DB
def createKeySet(public_key, private_key):
    salt = generateSalt()
    hash = hashKey(private_key, salt)

    existing = mongo.db.keys.find_one({"public_key": public_key})

    if existing is None:
        mongo.db.keys.insert({"public_key": public_key, "hash": hash,
        "salt": salt})
        return("Success")
    else:
        return("Username already taken.")

# List Converter for Converting Tags to a List
class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['list'] = ListConverter

# Create Keyset for Accessing Authenticated Information
@app.route("/create/<public_key>/<private_key>", methods = ['GET'])
def createUser(public_key, private_key):
    retrun(createKeySet(public_key, private_key))


# Dump All Information Regarding User
@app.route("/dump/<public_key>/<private_key>/<user>", methods = ['GET'])
def dumpUser(user, public_key, private_key_test):
    user_doc = mongo.db.id.find_one({"worker": user})
    requester = mongo.db.keys.find_one({"public_key": public_key})

    salt = requester["salt"]
    private_key_real = requester["hash"]

    if user_doc is None:
        return("User Not Found.")
    elif (hashKey(private_key, salt) == private_key_real):
        return(dumps(user_doc))
    else:
        return("Not Authenticated.")

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET'])
@app.route("/check/<user>/<list:tags>", methods = ['GET'])
def checkUserStatus(user, tags = "NA"):
    user_doc = mongo.db.id.find_one({"worker": user})

    if user_doc is None:
        return("User Not Found.")
    else:
        id = user_doc["_id"]
        mongo.db.id.update({ "_id" : id}, { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})

        return(str(user_doc["worker"]) + "," +  str(len(list(user_doc["pings"]))) + " " + str(tags))

# Method for Updating Tags Associated with User
@app.route("/update/<user>", methods = ['POST'])
def updateUserStatus(user):
    return "Testing"




@app.route("/")
def csv():
    return "Welcome to NaiveTurk"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', debug = True)
