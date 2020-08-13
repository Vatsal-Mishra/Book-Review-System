import os                                      # importing all the essential libraries
from sqlalchemy import create_engine                  # for the different parts of web application
from sqlalchemy.orm import scoped_session,sessionmaker
from flask_session import Session
from flask import session,Flask, render_template,request,redirect,url_for
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
engine=create_engine(os.getenv("DATABASE_URL")) # manages connection to database and sql commands
db=scoped_session(sessionmaker(bind=engine)) # create a scoped session thus creating individual session
@app.route("/")                              # for a particular user
def register():
    return render_template("registration.html") # the user will be taken to registration page
@app.route("/insert",methods=["POST"])
def insert():
    firstname=request.form.get("inputfirstname")     # taking all the information from the form entered by users
    lastname=request.form.get("inputlastname")
    username=request.form.get("username")
    email=request.form.get("inputEmail3")
    password=request.form.get("inputPassword3")
    try:
      db.execute("INSERT INTO users(firstname,lastname,username,email,password) VALUES(:firstname,:lastname,:username,:email,:password)",
                {"firstname":firstname,"lastname":lastname,"username":username,"email":email,"password":password})#inserting all the data in database and registering the user
      db.commit()
      return render_template('main.html',username=username)
    except:
        return render_template("error.html",message="Unexpected error occured ,check for \n 1-no entry is empty \n 2-username should be unique")#handling the error if user enters some wrong details
@app.route("/login")
def login():
    return render_template("login.html")   # registered user will be taken to login page
@app.route("/log",methods=["POST"])
def log():
    username=request.form.get("username")   # taking login details from the form
    password=request.form.get("inputPassword3")
    session["user_id"]=db.execute("SELECT id,username from users WHERE (username=:username AND password=:password)",{"username":username,"password":password}).fetchone()#keeping track of which user has logged in
    f=db.execute("SELECT username,password FROM users WHERE (username=:username AND password=:password)",{"username":username,"password":password}).fetchone()#validating the details from database if user exists
    if  f is None:
        return render_template('error.html',message='Error occured Please enter the valid username and password') #raising error if user is not registered
    else:
        return render_template('main.html',username=username,f=session["user_id"]) # after successful login taking user to the main page
@app.route("/search",methods=["POST"])
def search():
    username=session["user_id"][1]  # using session to get the username
    item=request.form.get("item")# getting the value from the searchbar
    if db.execute("SELECT * FROM books WHERE isbn LIKE '%"+item+"%' OR author LIKE '%"+item+"%' OR title LIKE '%"+item+"%'").rowcount==0: # checking for the appropriate response for the user
       return render_template("main.html" ,msg="Sorry didn't find anything ,please try again")
    else:
        searchitem=db.execute("SELECT * FROM books WHERE isbn LIKE '%"+item+"%' OR author LIKE '%"+item+"%' OR title LIKE '%"+item+"%'")
        return render_template("main.html",searchitem=searchitem,username=username,msg="You mean this---:")
@app.route("/bookpage/<int:id>/<string:title>" ,methods=["POST","GET"])
def bookpage(id,title):
    id1=session["user_id"][0]
    #if db.execute("SELECT * FROM reviews WHERE (title=:title)",{"title":title}).rowcount != 0 :
    h=db.execute("SELECT reviews.review,reviews.rate,users.username FROM reviews JOIN users ON reviews.id=users.id WHERE (title=:title)",{"title":title}) # qureying two tables simultaneously,getting all the prestored reviews for the particular book
    aboutbook=db.execute("SELECT * FROM books WHERE (id= :id)",{"id":id}).fetchall()
    if request.method == "POST" :
      rate=request.form.get("rate")  # getting the rate and review from the form entered by user
      review=request.form.get("review")
      if db.execute("SELECT * FROM  reviews WHERE (id=:id AND title=:title) ",{"id":id1,"title":title}).rowcount != 0 :  # checking whether the user has already given the review or not
             return render_template("bookpage.html",aboutbook=aboutbook,h=h,msg="You cannot give review twice")
      else:
             db.execute("INSERT INTO reviews(rate,review,title,id) VALUES(:rate,:review,:title,:id1)",{"rate":rate,"review":review,"title":title,"id1":id1})
             db.commit()
    #if db.execute("SELECT * FROM reviews WHERE (title=:title)",{"title":title}).rowcount != 0 :
    h=db.execute("SELECT reviews.review,reviews.rate,users.username FROM reviews JOIN users ON reviews.id=users.id WHERE (title=:title)",{"title":title})# finally giving all the reviews
    return render_template("bookpage.html",aboutbook=aboutbook,h=h)
@app.route("/logout")
def logout():
    session.clear()    # logging off the user
    return redirect(url_for("login")) # redirecting to log in page
