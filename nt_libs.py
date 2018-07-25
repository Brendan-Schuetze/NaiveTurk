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

# Other Utility Functions
import re
import requests

# Import Naive Turk Utility Functions
import nt_utils as nt

# Google Captcha Information
from captcha import *

# Start Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/turk"
app.secret_key = os.urandom(24)

# Access Database and Encryption Functions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# List Converter for Converting Tags to a List
class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split('+')

    def to_url(self, values):
        return '+'.join(BaseConverter.to_url(value)
                        for value in values)

app.url_map.converters['list'] = ListConverter
