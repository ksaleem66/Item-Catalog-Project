#!/usr/bin/env python3

'''
    File name: application.py
    Author: Khalid Saleem
    Date created: 08/03/2019
    Date last modified: 29/03/2019
    Description: a web application that provides a list of items within
    a variety of categories and integrate third party user registration and
    authentication.
    Python Version: 3.6.7
'''

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc, desc, DateTime
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Movie
import datetime
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = (json.loads(open('client_secrets.json', 'r').read())
             ['web']['client_id'])

APPLICATION_NAME = "Movie Category Menu Application"

# Connect to Database and create database session

engine = create_engine('sqlite:///moviecatalog.db',
                       connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state

#   Render the login.html template
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;\
    border-radius: 150px;-webkit-border-radius: 150px;\
    -moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
# on google


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps(
                                 'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps
                                 ('Failed to revoke token for given user.',
                                  400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Facebook connect method


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type =\
           fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=\
           %s' % (app_id, app_secret, access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace
        the remaining quotes with nothing so that it can be used directly
        in the graph pi calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = ('https://graph.facebook.com/v2.8/me?access_token=%s&fields=\
           name,id,email' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = ('https://graph.facebook.com/v2.8/me/picture?access_token=%s&\
           redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;\
               border-radius: 150px;-webkit-border-radius: 150px;\
               -moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output

# Facebook disconnect method


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
           % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Show all Categories and latest 5 items


@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).all()
    latest_items = session.query(Movie).order_by(desc(Movie.date)).limit(5)
    if 'username' not in login_session:
        return (render_template('public_showCategories.html',
                categories=categories, latest_items=latest_items))
    else:
        return (render_template('showCategories.html',
                categories=categories, latest_items=latest_items))

# Show selected Category Movie items and total count


@app.route('/category/<int:category_id>')
def showCategory(category_id):
    # Get all categories
    categories = session.query(Category).all()

    # Get selected category
    category = session.query(Category).filter_by(id=category_id).first()

    # Get name of category
    categoryName = category.name

    # Get all items of a specific category
    categoryMovies = (session.query(Movie).filter_by
                      (category_id=category_id).all())

    # Get count of category items
    categoryMoviesCount = (session.query(Movie).filter_by
                           (category_id=category_id).count())
    if 'username' not in login_session:
        return (render_template('public_showCategory.html',
                categories=categories, categoryMovies=categoryMovies,
                categoryName=categoryName,
                categoryMoviesCount=categoryMoviesCount))
    else:
        return (render_template('showCategory.html', categories=categories,
                categoryMovies=categoryMovies, categoryName=categoryName,
                categoryMoviesCount=categoryMoviesCount))

# Show selected Category Movie items


@app.route('/category/<int:category_id>/movies/<int:movie_id>')
def showCategoryMovie(category_id, movie_id):
    # Get category item
    categoryMovie = session.query(Movie).filter_by(id=movie_id).first()

    # Get creator of item
    #creator = getUserInfo(categoryMovie.user_id)
    return render_template('categoryMovie.html', categoryMovie=categoryMovie)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name'] == '':
            flash('Field cannot be blank, please try again')
            return redirect(url_for('showCategories'))
            # return render_template('newCategory.html')
        elif request.form['name'] != '':
            category = (session.query(Category).filter_by
                        (name=request.form['name']).first())
            if category is not None:
                flash('The entered category already exists.')
                return redirect(url_for('showCategories'))
            else:
                newCategory = (Category(name=request.form['name'],
                               user_id=login_session['user_id']))
                session.add(newCategory)
                session.commit()
                flash('New Category %s Successfully Added!' % newCategory.name)
                return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')

# Edit existing Category


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCategory.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized\
            to edit this category. Please create your own category in\
            order to edit.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)

# Delete existing Category


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not authorized\
                to delete this category. Please create your own category\
                in order to delete.'); }</script><body onload=\
                'myFunction()'>")
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('%s Category Successfully Deleted!' % categoryToDelete)
        return redirect(
            url_for('showCategories', category_id=category_id))
    else:
        return (render_template('deleteCategory.html',
                category=categoryToDelete))

# Add new Movie item


@app.route('/category/movie/add', methods=['GET', 'POST'])
def addNewMovie():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if not request.form['name']:
            flash('Please add Movie name')
            return redirect(url_for('addNewMovie'))
        if not request.form['description']:
            flash('Please add a description')
            return redirect(url_for('addNewMovie'))

        # Add movie item to Movie table
        newMovieItem = (Movie(name=request.form['name'],
                        description=request.form['description'],
                        category_id=request.form['category'],
                        date=datetime.date.today()))
        category = (session.query(Category).filter_by(
                    id=request.form['category']).one())
        if category.user_id != login_session['user_id']:
            return ("<script>function myFunction() {alert('You are not\
                    authorized to add movie items to this category.\
                    Please create your own category in order to add movies.')\
                    ;}</script><body onload='myFunction()'>")
        else:
            session.add(newMovieItem)
            session.commit()
            flash('New Movie Added Successfully!')
            return redirect(url_for('showCategories'))
    else:
        # Get all categories
        categories = session.query(Category).all()
        return render_template('addNewMovie.html', categories=categories)

# Edit existing Movie item


@app.route('/category/<int:category_id>/movie/<int:movie_id>/edit',
           methods=['GET', 'POST'])
def editMovieItem(category_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedMovie = session.query(Movie).filter_by(id=movie_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return ("<script>function myFunction() {alert('You are not authorized\
                to edit movie items of this category. Please create your own\
                category in order to edit movies.');}</script><body onload=\
                'myFunction()'>")

    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['description']:
            editedMovie.description = request.form['description']

        session.add(editedMovie)
        session.commit()
        flash('Movie Successfully Edited!')
        return redirect(url_for('showCategories'))
    else:
        return (render_template('editMovieitem.html', category_id=category_id,
                movie_id=movie_id, movie=editedMovie))

# Delete existing Movie item


@app.route('/category/<int:category_id>/movie/<int:movie_id>/delete',
           methods=['GET', 'POST'])
def deleteMovieItem(category_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    movieToDelete = session.query(Movie).filter_by(id=movie_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return ("<script>function myFunction() {alert('You are not authorized\
                to delete movie items of this category. Please create your own\
                category in order to delete movies.');}</script><body onload=\
                'myFunction()'>")

    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()
        flash('Movie Successfully Deleted!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteMovieitem.html', movie=movieToDelete)

# JSON


@app.route('/user/JSON')
def userJSON():
    users = session.query(User).all()
    return jsonify(users=[u.serialize for u in users])


@app.route('/category/JSON')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/movie/JSON')
def movieJSON():
    movies = session.query(Movie).all()
    return jsonify(movies=[m.serialize for m in movies])

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

# To run the flask web server


if __name__ == '__main__':
    app.secret_key = 'my_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
