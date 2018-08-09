execfile("nt_libs.py")

# Create Keyset for Accessing Authenticated Information
@app.route("/create/", methods = ['POST'])
def createUser():
    if nt.createKeySet(request.form['username'].upper(),
        request.form['password'],
        request.form['first_name'],
        request.form['last_name'],
        request.form['email_address']) == "Success.":
        return login()
    else:
        return("Failed to create account.")

# Account Creation Page
@app.route("/account/", methods = ['GET'])
def accountDetails():
    if not session.get('logged_in'):
        return render_template('account.html')
    else:
        return home()

@app.route("/settings/", methods = ['GET'])
def settings():
    if not session.get('logged_in'):
        return login()
    else:
        return(session.get('username'))

# Login Page
@app.route("/login/")
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return home()

# Method for Authenticating Username + Password Combo
@app.route("/authenticate/", methods = ['POST'])
def authenticate():
    remoteIP = request.environ['REMOTE_ADDR']
    response = request.form['g-recaptcha-response']

    params = {
        "secret": secret,
        "response": response,
        "remoteip": remoteIP
    }

    captchaCheck = requests.get(url = url, params = params)
    captchaCheck = captchaCheck.json()
    captchaResult = captchaCheck['success']

    if ((nt.authenticateRequester(request.form['username'].upper(), request.form['password'])) and captchaResult == True):
        session['logged_in'] = True
        session['username'] = request.form['username'].upper()
    elif captchaResult != True:
        return("Captcha failed.")
    else:
        return("Login could not be authenticated.")
    return redirect(nt.redirect_url())

# Dump All Information Regarding User (Admin Functionality)
@app.route("/dump/<user>/", methods = ['GET', 'POST'])
def dumpUser(user):
    user = nt.cleanInput(user)

    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and nt.authenticateRequester(request.form["username"].upper(), request.form["password"])):
        user_doc = nt.findWorker(nt.cleanInput(user))

        if user_doc is None:
            return("User Not Found.")
        else:
            return(dumps(user_doc))
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return login()

# Method for Checking if User is in Database
@app.route("/check/<user>/", methods = ['GET', 'POST'])
@app.route("/check/<user>/<list:tags>/", methods = ['GET', 'POST'])
def checkUserStatus(user, tags = None):
    user = nt.cleanInput(user)

    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and nt.authenticateRequester(request.form["username"].upper(), request.form["password"])):
        user_doc = nt.findWorker(nt.cleanInput(user))

        if user_doc is None:
            return("False")
        else:
            id = nt.pingWorker(user_doc)
            if tags is not None:
                for tag in tags:
                    tag_search = mongo.db.id.find({ "$and": [{"worker": nt.quickHash(user)}, {"tags.tag_name": tag}]})

                    if(tag_search.count() > 0):
                        return("True")
                    else:
                        tag_search = None

                return("False")
            else:
                return("True")
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return login()


# Method for Updating Tags Associated with User
@app.route("/add/<user>/<list:tags>/", methods = ['GET', 'POST'])
def updateUserStatus(user, tags):
    user = nt.cleanInput(user)

    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and nt.authenticateRequester(request.form["username"].upper(), request.form["password"])):
        user_doc = nt.findWorker(nt.cleanInput(user))
        if user_doc is None:
            mongo.db.id.insert({"worker": nt.quickHash(user),
                "time": strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                "pings": [],
                "tags": [],
                "private_tags": []
                })

            id = nt.pingWorker(nt.findWorker(user))

        else:
            id = nt.pingWorker(user_doc)

        #Private Tags Functions
        if "private" in tags:
            for tag in tags:
                mongo.db.id.update({ "_id" : id},
                { "$push": {
                        "private_tags": {
                        "tag_name": nt.quickHash(tag + session.get(['username'])),
                        "tag_time": strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        }}
                })
        else:
            for tag in tags:
                mongo.db.id.update({ "_id" : id},
                { "$push":{
                    "tags": {
                    "tag_name": tag,
                    "tag_time": strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    }}
                })

        return("Success.")
    elif request.method == "POST":
        return("Not Authenticated.")
    elif request.method == "GET":
        return(login())

@app.route("/add_file/", methods = ['GET', 'POST'])
def addFile():
    if (request.method == "GET" and session.get('logged_in')) or (request.method == "POST" and nt.authenticateRequester(request.form["username"].upper(), request.form["password"])):
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and nt.checkExtension(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file',
                                        filename=filename))
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <p><input type=file name=file>
             <input type=submit value=Upload>
        </form>
        '''
    else:
        return(login())

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return("Upload Succcessful") 
          


# Homepage
@app.route("/")
def home():
    return "Welcome to nvt.science"
    #return(nt.testImport())

if __name__ == "__main__":
    app.run(host ='0.0.0.0', debug = True)
