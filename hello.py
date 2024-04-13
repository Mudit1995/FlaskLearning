from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, SearchForm


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

# flask log in stuff 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass stuff to base.html because in the navbar.html we dont have the form but we are extending it in the base html therfore we are passing it to the base html
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# create the functino and route for the search page
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    post = Posts.query
    if form.validate_on_submit():
        # Get the data from the submitted form
        post.searched = form.searched.data
        # searched because oin the nav bar file we have given the name as searched
        # query the database
        posts = post.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template('search.html', form=form, searched = post.searched, posts = posts)
    else:
        return render_template('search.html', form=form, searched = post.searched)
    # form = PostForm()
    # if form.validate_on_submit():
    #     post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
    #     db.session.add(post)
    #     db.session.commit()
    #     flash("Blog Post Submitted Successfully")
    # return render_template('search.html', form=form)
 

# create a log in page 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash
            #  user.password_hash this is present in the database and will check the password against it 
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again")
        else:
            flash("User Does Not Exist")

    return render_template('login.html', form=form)

# log out page 
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('login'))

# create rthe dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():   
    form = UserForm()
    id = current_user.id
    #  the below will find the id of the user that we want to update quering on the user table ( which is actually act as a model)and then update the name and email into the database
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        # name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
        except:
            flash("Error! Looks like there was a problem...try again")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        # this will return the form and the user that we want to update with that once you hover to the update one then an id can also be seen in the left hand side of the screen
        return render_template('dashboard.html', form=form, name_to_update=name_to_update,id=id)
    

# create a blog post model 
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # creating the foreign key which will reference the primary key for the user table
    # over here the users is referencing to the database users table not the class Users that is why it is in short hands as db.ForeignKey('users.id') 
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# route to the delere the post 
@app.route('/posts/delete/<int:id>',endpoint='delete_post')
@login_required
def delete(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            # Return a message 
            flash('Post was deleted')

            # grab all the posts from the database
            posts = Posts.query.order_by(Posts.date_posted).all()
            return render_template('posts.html', posts=posts)
        except:
            # Return an error message
            flash('There was an issue deleting that post')
            posts = Posts.query.order_by(Posts.date_posted).all()
            return render_template('posts.html', posts=posts)
    else:
        flash('You are not authorized to delete that post')
        posts = Posts.query.order_by(Posts.date_posted).all()
        return render_template('posts.html', posts=posts)



# ceate a blog page 
@app.route('/posts')
def posts():
    # grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted).all()
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# edit a post route
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    # the logic is we are taking the post from the database and displaying it in the form and that post has the id associated 
    # with it which can be only accesed by the user who created it using the poster id
    # and the post refence as the poster and if the potser user id is equal to the current user id then we can edit the post
    post = Posts.query.get_or_404(id)
    form = PostForm()
    
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.content = form.content.data
        post.slug = form.slug.data
        # update the database
        db.session.add(post)
        db.session.commit()
        flash('Post has been updated')
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id:
        # this is for when we edit the post which is already in the database therefore when this page loads it will show the data that is already in the database
        form.title.data = post.title
        # form.author.data = post.author
        form.content.data = post.content
        form.slug.data = post.slug
        return render_template('edit_post.html', form=form)
    else:
        flash('You are not authorized to edit this post')
        posts = Posts.query.order_by(Posts.date_posted).all()
        return render_template('posts.html', posts=posts)


# Add a post Page
@app.route('/add-post', methods=['GET', 'POST'])

def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            slug=form.slug.data
        )
        # Clear the form and redirect to that page 
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)




class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    password_hash = db.Column(db.String(128), nullable=False)

    # users can have many posts 
    #  over ehere the Posts is refernecing the Posts model class not the name of the table in the database
    posts = db.relationship('Posts', backref='poster', lazy=True)

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

            user = Users(name=form.name.data, username = form.username.data ,email=form.email.data,favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        # after adding the data we need to clear the form.
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        # flash("User Added Successfully!"


        flash("User Added Successfully!")
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
@login_required
def update(id):
    form = UserForm()
    #  the below will find the id of the user that we want to update quering on the user table ( which is actually act as a model)and then update the name and email into the database
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        # name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            # after submitting the form we are taking the user to the dashboard.
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)
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



# create the passward test Page 
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # validate the form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        # lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()
        # check hashed password
        if pw_to_check is not None:
            passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template('test_pw.html', email=email, password=password, pw_to_check=pw_to_check, passed = passed ,form=form)

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
 













  