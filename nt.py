from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
mongo = PyMongo(app)

@app.route("/r/<user>", methods = ['GET'])
def returnUserStatus(user):
    


@app.route("/r/<user>", methods = ['POST'])
def updateUserStatus(user):




@app.route("/")
def csv():
    return "Welcome to NaiveTurk"
 
if __name__ == "__main__":
    app.run(host ='0.0.0.0')

