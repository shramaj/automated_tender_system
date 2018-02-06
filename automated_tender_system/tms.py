from flask import Flask, render_template, url_for, request, session, redirect
import json
import random
import string
from flask_pymongo import PyMongo,ObjectId
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message, Mail
import bcrypt
import threading
from datetime import datetime
import smtplib
import re
import time

app = Flask(__name__)
app.config.from_object(__name__)
mail = Mail(app)

app.config['MONGO_DBNAME'] = 'users'
app.config['MONGO2_DBNAME'] = 'fci'
mongo2 = PyMongo(app, config_prefix='MONGO2')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'tms.sih2017@gmail.com'
app.config['MAIL_PASSWORD'] = 'tmssih123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'
app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'

mongo = PyMongo(app)

# @app.route('/settime')
# def timeconvert():
#     datetimestring = mongo2.db.tenders_fci.find({},{"epub_date":1,"_id":1})
#     for t in datetimestring:
#         timestamp = time.mktime(time.strptime(t['epub_date'], '%d-%b-%Y %I:%M %p'))
#         mongo2.db.tenders_fci.update({"_id":t['_id']},{"$set":{"epub_date":timestamp}})


class myThread (threading.Thread):
    def __init__(self, to, subject, msg):
        threading.Thread.__init__(self)
        self.to = to
        self.subject = subject
        self.msg = msg

    def run(self):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("tms.sih2017@gmail.com", "tmssih123")
        message = 'Subject: {}\n\n{}'.format(self.subject, self.msg)
        server.sendmail("tms.sih2017@gmail.com", self.to, message)
        server.quit()

@app.route('/',methods=['GET'])
def index():
    if 'loginid' in session:
        return render_template('index.html', loginid = session['loginid'])
    return render_template('index.html', session = session)
    


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        companies = mongo.db.companies
        dept = mongo.db.dept
        login_user = companies.find_one({'loginid': request.form['l_ID']})
        logged_dept = dept.find_one({'nEmail': request.form['l_ID']})
        if login_user and login_user['confirmed']==True:
            if bcrypt.hashpw(request.form['pwd'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['loginid'] = login_user['cName']
                return redirect(url_for('profile'))
        elif logged_dept:
            if bcrypt.hashpw(request.form['pwd'].encode('utf-8'), logged_dept['password']) == logged_dept['password']:
                session['loginid'] = logged_dept['dName']
                return redirect(url_for('profile_nodal'))       
        return 'Invalid username/password combination or Email ID not verified'
    return render_template('login.html')


@app.route('/forgot_pass',methods=['POST','GET'])
def forgot_pass():
    if request.method == 'POST':
        companies = mongo.db.companies
        login_user = companies.find_one({'loginid': request.form['l_ID']})

        if login_user and login_user['confirmed']==True:
            token = generate_confirmation_token(request.form['l_ID'])
            confirm_url = url_for('new_pass', token=token, _external=True)
            # html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Enter your new password!"
            print("hrllo")
            new_thread = myThread(request.form['l_ID'],subject,confirm_url)
            new_thread.start()
            return redirect(url_for('index'))
        return 'That username already exists!'
    return render_template('forgot_pass.html')

@app.route('/new_pass/<token>',methods=['POST','GET'])
def new_pass(token):
    email=confirm_token(token)
    if request.method == 'POST':
        hashpass = bcrypt.hashpw(request.form['pwd'].encode('utf-8'), bcrypt.gensalt())
        companies = mongo.db.companies
        login_user = companies.find_one({'loginid':email})
        companies.update({'loginid':email},{"$set":{'password': hashpass}})
        return render_template('login.html')
    return render_template('new_pass.html',token=token)
    # return "OK"



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])



def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        print('The confirmation link is invalid or has expired.', 'danger')
    user = mongo.db.companies.find_one({'cMail':email})         
    if user['confirmed']==True:
        print('Account already confirmed. Please login.', 'success')
    else:
        mongo.db.companies.update({"cMail":email},{"$set":{"confirmed":True}})
        # user.confirmed_on = datetime.datetime.now()
        session['username'] = user['loginid']
        #db.session.commit()
        print('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('faq'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        companies = mongo.db.companies
        existing_user = companies.find_one({'loginid': request.form['l_ID']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pwd'].encode('utf-8'), bcrypt.gensalt())
            companies.insert(
                {'loginid': request.form['l_ID'],'password':hashpass, 'cName': request.form['cName'], 'cRnum': request.form['cRnum']
                    , 'cAddr': request.form['cAddr'], 'nPart': request.form['nPart'], 'city': request.form['city'],
                 'state': request.form['state'], 'pCode': request.form['pCode'], 'pan': request.form['pan'],
                 'eYear': request.form['eYear'], 'nob': request.form['nob'], 'lStat': request.form['lStat'],
                 'cMail': request.form['cMail'], 'pNum': request.form['pNum'], 'mNum': request.form['mNum'], 'confirmed':False})
            # session['username'] = request.form['l_ID']
            token = generate_confirmation_token(request.form['cMail'])
            confirm_url = url_for('confirm_email', token=token, _external=True)
            # html = render_template('activate.html', confirm_url=confirm_url)
            subject = "Please confirm your email"
            #send_email(request.form['cMail'],subject,confirm_url)
            new_thread = myThread(request.form['cMail'],subject,confirm_url)
            new_thread.start()
            return redirect(url_for('index'))
        return 'That username already exists!'
    return render_template('register.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/logout')
def logout():
    if 'loginid' in session:
    # remove the username from the session if it is there
        session.pop('loginid', None)
        return redirect(url_for('index'))
    return "OK"

@app.route('/latest')
def latest():
    tender_list = (mongo2.db.tenders_fci.find().sort("epub_date",-1).limit(10))
        # tender_list = mongo2.db.tenders_fci.find({"$text": {"$search": search_this_string}})
    output = []
    for tender_element in tender_list:
        output.append(tender_element)
    return render_template('latest.html',list_of_tenders = output)
    





@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        mongo2.db.tenders_fci.create_index([('org_chain', 'text'),('title','text'),('description','text')])
        search_this_string = request.form['srch-term']
        type_filter = request.form['tender_type']
        status_type = request.form.getlist('status_type')
        sort_by = request.form['sort_by']
        if type_filter == "None":
           type_filter = re.compile("^", re.IGNORECASE) 
        if len(status_type)==0:
            status_type = ['Active','Archive','Corrigendum']
        tender_list = (mongo2.db.tenders_fci.find({"$text": {"$search": search_this_string}, "type": type_filter, "status":{"$in":status_type}}))
        # tender_list = mongo2.db.tenders_fci.find({"$text": {"$search": search_this_string}})
        output = []
        for tender_element in tender_list:
            print(tender_element)
            output.append(tender_element)
        return render_template('search.html',list_of_tenders = output)
    return render_template('search.html')

@app.route('/tender_page/<token>',methods=['POST','GET'])
def tender_page(token):
    if 'loginid' in session:
        if request.method == 'POST':
            cName = session['loginid']
            var = mongo.db.applications.find_one({"cName":cName})
            if var['state'] is not "blacklisted":
                mongo.db.applications.update_one({'cName':cName}, {'$set':{"tender_id":ObjectId(token), "time":datetime.now()}}, upsert=True)
            # mongo.db.applications.insert({"cName":session['_id'],{"$addToSet":{"applied_tenders":token, }})
            return redirect(url_for('index'))
    result = mongo2.db.tenders_fci.find_one({"_id":ObjectId(token)})
    return render_template('tender_page.html', tender_details=result)
    # return render_template('tender_page.html',final_comments = result)
    # return render_template('tender_page.html',token = token)
    # return token


@app.route('/tender_list')
def tender_list():
    list_of_tenders = mongo2.db.tenders_fci.find({},{"_id":1,"id":1,"title":1,"opening_date":1, "org_chain":1})
    return render_template('tender_list.html',list_of_tenders =list_of_tenders)


@app.route('/profile',methods=['POST','GET'])
def profile():
    if 'loginid' in session:
        logged_company = mongo.db.companies.find_one({'cName':session['loginid']})
        logged_dept = mongo.db.dept.find_one({'dName': session['loginid']})
        logged_admin = mongo.db.companies.find_one({'loginid': session['loginid']})

        if logged_company is not None:
            if request.method=='POST':
                hashpass = bcrypt.hashpw(request.form['pwd'].encode('utf-8'), bcrypt.gensalt())
                mongo.db.companies.update({"cName": session['loginid']}, {"$set": {"city": request.form['city'], 
                    'pCode': request.form['pCode'], 'pan': request.form['pan'], 'eYear': request.form['eYear'], 'nob': request.form['nob'],
                    'cMail': request.form['cMail'], 'pNum': request.form['pNum'], 'mNum': request.form['mNum'], 'password':hashpass  }})
            companies = mongo.db.companies
            login_user = companies.find_one({'cName': session['loginid']})
            # print(login_user)
            return render_template('profile.html', login=login_user)
        elif logged_dept is not None:
            if request.method == 'POST':
                dept = mongo.db.dept
                dept.update({"dName": session['loginid']}, {"$set": {"name": request.form['Name'],
                                    'email': request.form['email'], 'ph_no': request.form['ph_no']}})
                dept = mongo.db.dept
                login_user1 = dept.find_one({'dName': session['loginid']})
                print(login_user1)
                return render_template('profile_nodal.html', login=login_user1)
        elif logged_admin is not None:
            if request.method == 'POST':
                mongo.db.companies.update({"loginid": session['loginid']}, {"$set": {"name": request.form['Name'],
                                    'email': request.form['email'], 'ph_no': request.form['ph_no']}})
                return render_template('profile_admin.html', login=admin_data)
    return redirect(url_for('login'))

@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        dept = mongo.db.dept
        existing_dept = dept.find_one({'dName': request.form['dName']})
        chars=string.ascii_letters + string.digits
        pwdSize=8
        randpass = ''.join((random.choice(chars)) for x in range(pwdSize))
        if existing_dept is None:
            hashpass = bcrypt.hashpw(randpass.encode('utf-8'), bcrypt.gensalt())
            dept.insert(
                {'dName': request.form['dName'], 'name': request.form['name'],
                 'nCon': request.form['nCon']
                    , 'nEmail': request.form['nEmail'], 'nAddr': request.form['nAddr'], 'password': hashpass})
            subject = "Your account is added"
            msg = "your password is:" + randpass
            #send_email(request.form['nEmail'], subject, msg )
            new_thread1=myThread(request.form['nEmail'],subject,msg)
            new_thread1.start()
            return redirect(url_for('admin'))
    return render_template('addusers.html')

def admin():
    session['loginid'] = "Admin"
    if session['loginid'] == "Admin":
        companies = mongo.db.companies
        admin_data = companies.find_one({'loginid': session['loginid']})
        print(admin_data)
        return render_template('profile_admin.html', login=admin_data)
    return redirect(url_for('login'))


@app.route('/active')
def active():
    tender_list = mongo2.db.tenders_fci.find({'status':'Active'})
    output = []
    for tender_element in tender_list:
        output.append(tender_element)
    return render_template('active_tenders.html', list_of_tenders=output)


@app.route('/closed')
def closed():
    tender_list = mongo2.db.tenders_fci.find({'status':'Closed'})
    output = []
    for tender_element in tender_list:
        output.append(tender_element)
    return render_template('closed_tenders.html', list_of_tenders=output)


@app.route('/applications')
def applications():
    if 'loginid' in session:
        dept = mongo.db.dept
        login_user1 = dept.find_one({'dName': session['loginid']})
        output = []
        if login_user1 is not None:
            application_list = mongo.db.applications.find()
            for application_element in application_list:
            # print(tender_element)
                output.append(application_element)
        return render_template('applications.html',list_of_applications = output)
    return render_template("login.html")

@app.route('/detail_app/<token>',methods=['POST','GET'])
def detail_app(token):
    if 'loginid' in session:
        dept = mongo.db.dept
        login_user1 = dept.find_one({'dName': session['loginid']})
        if login_user1 is not None:
            result = mongo.db.applications.find_one({"_id":ObjectId(token)})
            customer = mongo.db.companies.find_one({"cName":result['cName']})
            if request.method == 'POST':
                mongo.db.applications.update({"_id":ObjectId(token)},{"$set":{"state":request.form['state']}})
                # mongo2.db.user.companies({"cName": request.},{"$set": {"state":request.form['state'] }})
            return render_template('detail_app.html',details =result, customer_details =customer)
    return render_template('login.html')




@app.route('/view_tenders')
def view_tenders():
    if 'loginid' in session:
        dept = mongo.db.dept
        login_user1 = dept.find_one({'dName': session['loginid']})
        if login_user1 is not None:
            tender_list = mongo2.db.tenders_fci.find()
            output = []
            for tender_element in tender_list:
                output.append(tender_element)
            return render_template('view_tenders.html',list_of_tenders =output)
    return render_template('login.html')

@app.route('/display_deadline')
def display_deadline():
    return render_template('display_deadline.html')


@app.route('/task/<token>',methods=['POST'])
def task(token):
    if 'loginid' in session:
        if request.method == 'POST':
            tenders_fci.update({'_id':ObjectId(token)},{"$set":{"task":{"task1":request.form["task1"],"deadline1":request.form['date1'],"task2":request.form['task2'],
                                "deadline2":request.form['date2'],'task3': request.form['task3'],"deadline3":request.form['date3'],'task4':request.form['task4'],
                                "deadline5":request.form['date5'],}}})

    return render_template('task.html',token =token)

@app.route('/criteria/<token>',methods=['POST','GET'])
def criteria(token):
    if 'loginid' in session:
        print('in session criteria')
        if request.method == 'POST':
            print('in post criteria')
            tenders_fci=mongo2.db.tenders_fci
            tenders_fci.update({'_id':ObjectId(token)},{"$set":{"criteria":{"criteria1":request.form["criteria1"] ,"criteria2":request.form['criteria2'],
                             'criteria3': request.form['criteria3'],'criteria4':request.form['criteria4']}}})
            return render_template('profile_nodal.html',token=token)
        return render_template('criteria.html',token =token)
    return redirect(url_for('login'))

@app.route('/tender_page_nodal/<token>',methods=['POST','GET'])
def tender_page_nodal(token):
    if 'loginid' in session:
        if request.method == 'POST':
            if request.form['Submit'] == "Submit":
                return redirect(url_for('criteria',token = token))
            elif request.form['Submit']== "progress":
                return render_template('task.html',token=token)
    result = mongo2.db.tenders_fci.find_one({"_id":ObjectId(token)},)
    # setval = 0
    # if result['criteria'] is not None :
    #     setval =1
        # return render_template('criteria.html',token =token, setval = setval)
    return render_template('tender_page_nodal.html', tender_details=result)

@app.route('/blacklisted')
def blacklisted():
    result = mongo.db.applications.find({"state":"blacklisted"})

    return render_template('blacklisted.html',result = result)


@app.route('/profile_nodal')
def profile_nodal():
    if 'loginid' in session:
        print('in profile_nodal')
        dept = mongo.db.dept
        login_user1 = dept.find_one({'dName': session['loginid']})
        return render_template('profile_nodal.html', login=login_user1)
    return redirect(url_for('login'))

@app.route('/feedback',methods=['POST','GET'])
def feedback():
    if 'loginid' in session:
        print('into session!!!!!!!!!!!!!!')
        if request.method == 'POST':
            dept=mongo.db.dept 
            dept1 = dept.find_one({'dName': request.form['to']})
            subject="Feedback from" + " "+session['loginid'] +" "+request.form['sub']
            msg=request.form['msg']
            new_thread1=myThread(dept1['nEmail'],subject,msg)
            new_thread1.start()
            return redirect(url_for('index'))
        return render_template('feedback.html')
    return render_template('login.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', debug=True)
