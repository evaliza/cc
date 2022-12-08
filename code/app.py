from cgitb import html
import mysql.connector  # pip install mysql-connector-python
import pickle
from numpy import imag
import requests
from camera import VideoCamera
import hashlib #MD5
from flask import Flask, render_template, redirect, request, session, Response, url_for
from flask_session import Session
import flask_monitoringdashboard as dashboard
#from bs4 import BeautifulSoup

app = Flask(__name__)

# monotoring
dashboard.config.init_from(file='config.cfg') #  In order to configure the Dashboard with a configuration-file,
dashboard.bind(app) # add monotoring

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

s = requests.Session()
def connector():
    mydb = mysql.connector.connect(
        host = "localhost",
        user= "root",
        passwd="MYsql",
        database= "ASL"
    )
    return mydb

def identification(connect, email, pwd):
     c = connect.cursor()
     requete = 'SELECT name, email, role_id FROM user WHERE email="'+email+'" and password="'+pwd+'"'
     c.execute(requete)
     result = c.fetchone()
     
     return result

def createUser(connect, name, lastname, email, pwd, role):
    c = connect.cursor()
    requete = 'INSERT INTO user (name, lastname, email, password, role_id) VALUES ("'+name+'","'+lastname+'","'+email+'","'+pwd+'","'+role+'")'
    c.execute(requete)
    connect.commit()

def updateUser(connect, id, name, lastname, email, pwd, role):
    c = connect.cursor()
    requete = 'UPDATE user SET name="'+name+'", lastname="'+lastname+'", email="'+email+'", password="'+pwd+'", role_id="'+role+'" WHERE id ="'+id+'"'
    c.execute(requete)
    connect.commit()

def deleteUser(connect, id):
    c = connect.cursor()
    requete = 'DELETE FROM user WHERE id ="'+id+'"'
    c.execute(requete)
    connect.commit()



def gen(camera):
    while True:
        frame = camera.get_frame_hand()
        yield (b'--frame\r\n'
            b'Content - Type: image/jpeg\r\n\r\n' + frame
            + b'\r\n\r\n')

# The route
@app.route('/cam/', methods=['GET', 'POST'])
def cam():
    try:
        return render_template('cam.html')

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print("Unexpected {err=}, {type(err)=}")
        raise    
        
    msg = ''
    return render_template('login.html', msg='')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/deconnection')
def deconnection():
    session.clear()
    return render_template('deconnection.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    #identification = 0
    try:
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
            email = request.form['email'].strip()
            pwd = request.form['password'].strip()
            pwd = hashlib.md5(pwd.encode()).hexdigest()
            print("email :", email)
            print("pwd :", pwd)

            # connexion à la BDD mySql 
            connect = connector()
            r = identification(connect, email, pwd)
            print("reponse:",r)
            if r is not None:
                session['name'] = r[0]
                session['email'] = r[1]
                session['role'] = r[2]
                return redirect(url_for('cam', code=302))

            # Select all info the movies
            #titlesdb = get_movie_titles(connect)
            
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print("Unexpected {err=}, {type(err)=}")
        raise    
        
    return render_template('login.html')

@app.route('/create_user/', methods=['GET', 'POST'])
def create_user():
    connect = connector()
    try:
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
            name = request.form['name'].strip()
            lastname = request.form['lastname'].strip()
            email = request.form['email'].strip()
            pwd = request.form['password'].strip()
            doneUser = request.form['doneUser'].strip()
            pwd = hashlib.md5(pwd.encode()).hexdigest()
            print("mot de passe :", pwd)
            role = request.form['role']
            print("email :", email)            
            print("#### insert")
            createUser(connect, name, lastname, email, pwd, role)

            if doneUser == "1":
                session['name'] = name
                session['email'] = email
                session['role'] = 1
                return redirect(url_for('cam', code=302))

            return render_template('list_user.html')
    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
    
    c = connect.cursor()
    c.execute("SELECT id,name FROM role")
    return render_template('create_user.html', roles=c.fetchall())

@app.route('/update_user/', methods=['GET', 'POST'])
def update_user():
    connect = connector()
    try:
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            id =  request.form['id'].strip()
            name = request.form['name'].strip()
            lastname = request.form['lastname'].strip()
            email = request.form['email'].strip()
            pwd = request.form['password'].strip()
            pwd = hashlib.md5(pwd.encode()).hexdigest()
            print("mot de passe :", pwd)
            role = request.form['role']
            print("email :", email)

            # connexion à la BDD mySql 
            
            print("#### update")
            updateUser(connect, id, name, lastname, email, pwd, role)
            # Select all info the movies
            #titlesdb = get_movie_titles(connect)
            msg = ''
            return render_template('modification_user.html', msg='')

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")

    return render_template('create_user.html', roles=c.fetchall())

@app.route('/delete_user/', methods=['GET', 'POST'])
def delete_user():
    connect = connector()
    try:
        if request.method == 'POST' and 'id' in request.form :
            id =  request.form['id'].strip()

            print("#### delete")
            deleteUser(connect, id)
            # Select all info the movies
            #titlesdb = get_movie_titles(connect)
            msg = ''
            return render_template('modification_user.html', msg='')

    except OSError as err:
        print("OS error: {0}".format(err))
    except ValueError:
        print("Could not convert data to an integer.")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
    raise

@app.route('/list_user/', methods=['GET', 'POST'])
def list_user():
    connect = connector()
    c = connect.cursor()
    c.execute("SELECT * FROM user")
    return render_template('list_user.html', roles=c.fetchall())

@app.route('/monotoring/', methods=['GET', 'POST'])
def monotoring():
    return render_template('monotoring.html')
    

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        connect = connector()
        return render_template("index.html")

    return render_template('index.html')

if __name__ == "__main__": 
    app.debug = True
    app.run()
