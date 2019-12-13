import os

# Andres Orozco 
from collections import deque

from flask import Flask, render_template, session, request, redirect
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helpers import login_required

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)

# List to keep the created channels 
channelsCreated = []

# List to save logged users
usersLogged = []

# Instanciate a dict
channelsMessages = dict()

@app.route("/")
@login_required
def index():

    return render_template("index.html", channels=channelsCreated)

# Sign in page saving username with cookies 
@app.route("/signin", methods=['GET','POST'])
def signin():

    #Forget any username 
    session.clear()

    username = request.form.get("username")
    
    if request.method == "POST":

        if len(username) < 1 or username is '':
            return render_template("error.html", message="username can't be empty.")

        if username in usersLogged:
            return render_template("error.html", message="that username already exists!")                   
        
        usersLogged.append(username)
        session['username'] = username
        session.permanent = True

        return redirect("/")
    else:
        return render_template("signin.html")

# Log out and remove user cookies !IMPORTANT !LOGOUT BEFORE CLOSING THE BROWSER! 
@app.route("/logout", methods=['GET'])
def logout():

    try:
        usersLogged.remove(session['username'])
    except ValueError:
        pass

    session.clear()

    return redirect("/")


# Create a new channel and also redirect to it page
@app.route("/create", methods=['GET','POST'])
def create():

    newChannel = request.form.get("channel")

    if request.method == "POST":
        if newChannel in channelsCreated:
            return render_template("error.html", message="that channel already exists!")
        
        # Append new channel to the list of channels
        channelsCreated.append(newChannel)
        channelsMessages[newChannel] = deque()

        return redirect("/channels/" + newChannel)
    
    else:

        return render_template("create.html", channels = channelsCreated)

# Channel page 
@app.route("/channels/<channel>", methods=['GET','POST'])
@login_required
def enter_channel(channel):
    
    # Join user to selected channel 
    session['current_channel'] = channel

    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("channel.html", channels= channelsCreated, messages=channelsMessages[channel])


# User joined message
@socketio.on("joined", namespace='/')
def joined():
    
    room = session.get('current_channel')
    join_room(room)
    
    emit('status', {
        'userJoined': session.get('username'),
        'channel': room,
        'msg': session.get('username') + ' has entered the channel'}, 
        room=room)

# User left mesage
@socketio.on("left", namespace='/')
def left():
    """ Send message to announce that user has left the channel """

    room = session.get('current_channel')

    leave_room(room)

    emit('status', {
        'msg': session.get('username') + ' has left the channel'}, 
        room=room)

# Recieve the message and print it
@socketio.on('send message')
def send_msg(msg, timestamp):

    # Print it only to users in the same channel
    room = session.get('current_channel')

    # To save the last 100 messages
    if len(channelsMessages[room]) > 100:
        # Pop the oldest message
        channelsMessages[room].popleft()

    channelsMessages[room].append([timestamp, session.get('username'), msg])

    emit('announce message', {
        'user': session.get('username'),
        'timestamp': timestamp,
        'msg': msg}, 
        room=room)