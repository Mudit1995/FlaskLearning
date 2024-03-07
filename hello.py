from flask import Flask, render_template



# created the flask app instance. this helps find all the files and directories. this also helps to run the app or the flask project 
app = Flask(__name__)

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

# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)
