from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# created the flask app instance. this helps find all the files and directories. this also helps to run the app or the flask project 

app = Flask(__name__)

# add database 
 # this is the URL of the database in future we can change it if we requre it as well.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# sectrte key is used to encrypt the session
app.config["SECRET_KEY"] = "Mudit1995 super scetrt key "


# initialize the database
db = SQLAlchemy(app)
# crate a model -> tell us what we gonna save into the database the model is a blueprint like a class what actually our app will gonna do 
# so we have create the model and then we have created the database and then we have created the table in the database using the createall function and 
# then we have created the user form and now we will craete the route to that form. 
migrate = Migrate(app, db) 

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128), nullable=False)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    

    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string
    def __repr__(self):
        return '<Name %r>' % self.name
with app.app_context():
    # Inside the application context
    db.create_all()
    
#  create a form which will take all the input from the user and save it in the database
    # vakidor checks weather the field is empty or not if the field is empty then it will not save the data in the database.
class UserForm(FlaskForm):

    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords Must Match")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# create the route for the form
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        # this is where we are receiving the details of the blogger from the form in the front end  
        if user is None:
            # hash the password
            # hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")

            user = Users(name=form.name.data, email=form.email.data,favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        # after adding the data we need to clear the form.
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        # flash("User Added Successfully!"
        flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added) 
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

#uodate the record in the database
# geneeally one route is the where uit will take to the next page so when we are defining the function name generally is the HTML page where it will gonna take us
# when we need to update the record in the database we need to use both the request post and get 
# This code snippet is a Flask route that handles the "/update/int:id" endpoint. It accepts both GET and POST requests.
# In the GET request, it initializes a form object and retrieves the user with the specified ID from the database. It then renders the "update.html" template, passing the form and the user object to the template.
# In the POST request, it updates the name and email fields of the user object with the values submitted in the form. 
# It then tries to commit the changes to the database. If the commit is successful, it flashes a success message and renders 
# the "update.html" template again. If there is an error during the commit, it flashes an error message and also renders the "update.html" template.
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    #  the below will find the id of the user that we want to update quering on the user table ( which is actually act as a model)and then update the name and email into the database
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem...try again")
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        # this will return the form and the user that we want to update with that once you hover to the update one then an id can also be seen in the left hand side of the screen
        return render_template('update.html', form=form, name_to_update=name_to_update,id=id)


# delete the record in the database
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")
        our_users = Users.query.order_by(Users.date_added) 
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("Error! Looks like there was a problem...try again")
        return render_template('add_user.html', form=form, name=name, our_users=our_users,id = id)


# try to vreate the db connectivity ib the database MYSQL 


# crearing a form class and use it whwenwve we want by calling the funciton 
#  the first step is we will create the CSRF token which is behind the scenes asssociated with the form 
class NameForm(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# @app.route('/')

#  lets create a route decroator 
#  route decorator is used to tell the flask what url should be used to call this function
#  the home page is this
# @app.route('/')
# def index():
#     return "<h1> hello world </h1> <h2> mudit </h2>"


# '''
#  Some examples of jinja tags 
#  safe -- in this tag we can write html code in it which dosnt allow html to come in on the front end but actualy its effect can be seen
#  trim -- remove the trailing white spaces
#  striptags - this will remove the html tags in the string
#  lower 
#  upper
#  title
#  replace
#  '''

@app.route('/')
def index():
    fisrt_name = "mudit"
    stuff = "This is <strong>bold </strong> text"
    favorite_pizza = ["peperoni", "cheese", "tomato"]

    return render_template('index.html', fisrt_name=fisrt_name,stuff = stuff, favorite_pizza = favorite_pizza)


# #localhost:5000/users/mudit

# this is jinja template that we use where we are passing the name of the user to the HTML template 
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# create custom error pages
# Invalid URL
# 404 Error -- page not found flask has the something ehwhich we called as error handlenr for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error thing
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#  creating a form route 
#  creating a form class


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully!")
    return render_template('name.html', name = name, form = form)



if __name__ == "__main__":
    app.run(port=8000, debug=True)
 