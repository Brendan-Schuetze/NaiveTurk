# Import Libraries
from flask import Flask
from flask_pymongo import PyMongo
from time import gmtime, strftime
from werkzeug.routing import BaseConverter

# Start Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
mongo = PyMongo(app)

# List Converter for Converting Tags to a List
class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['list'] = ListConverter

@app.route("/dump/<user>/", methods = ['GET'])
def dumpUser(user, tags = "NA"):
    user_doc = mongo.db.id.find_one({"worker": user})

    if user_doc is None:
        return("User not found")
    else:
        return(json.dumps(user_doc, indent = 4))

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET'])
@app.route("/check/<user>/<list:tags>", methods = ['GET'])
def checkUserStatus(user, tags = "NA"):
    user_doc = mongo.db.id.find_one({"worker": user})

    if user_doc is None:
        return("User not found")
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
