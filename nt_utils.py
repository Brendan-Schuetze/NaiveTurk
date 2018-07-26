execfile("nt_libs.py")

# Test
def testImport():
    return("success")

# Clean input
def cleanInput(input):
    input = input.upper()
    input = re.sub("{|}", "", input).replace('"',"")
    return(input)

# Password Hashing Function
def slowHash(key):
    hash = bcrypt.generate_password_hash(key)
    return(hash)

# Username Hashing Function
def quickHash(user):
    user = hashlib.sha256(user + "421863908668nvt.science438528981179").hexdigest()
    return(user)

# Helper Function for Generating Hashes and Inserting into DB
def createKeySet(public_key, private_key, first_name, last_name, email_address):
    hash = slowHash(private_key)

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
    return(mongo.db.id.find_one({"worker": quickHash(user)}))

# Ping Worker
def pingWorker(user_doc):
    id = user_doc["_id"]
    mongo.db.id.update({ "_id" : id},
        { "$push": { "pings": strftime("%Y-%m-%d %H:%M:%S", gmtime()) }})
    return(id)

# Update Worker Tags
def pingTag(id, tag):
    return(True) # TODO: Finish this

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

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
