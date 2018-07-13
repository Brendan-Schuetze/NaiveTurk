from flask import Flask
from flask_pymongo import PyMongo
from time import gmtime, strftime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
mongo = PyMongo(app)

@app.route("/r/<user>", methods = ['GET'])
def returnUserStatus(user): 
    user_doc = mongo.db.id.find_one({"worker": user})
 
    if user_doc is None:
        return("User not found")
    else: 
        id = user_doc["_id"]
        mongo.db.id.update({ "_id" : id}, { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})        
        
        return(str(user_doc["worker"]) + "," +  str(len(list(user_doc["pings"]))))   


@app.route("/r/<user>", methods = ['POST'])
def updateUserStatus(user):
    return "Testing"




@app.route("/")
def csv():
    return "Welcome to NaiveTurk"
 
if __name__ == "__main__":
    app.run(host ='0.0.0.0', debug = True)

