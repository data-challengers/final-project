import os
import flask
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pyvis.network import Network
import networkx as nx
import unwrapped.genre_network as gn
import unwrapped.streamgraph as sg
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


import json

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,
    static_folder='data')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'unwrapped.sqlite'),
    )
    UPLOAD_FOLDER = app.root_path + '/data/uploads/'
    ALLOWED_EXTENSIONS = {'json'}

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route("/")
    # def index():
    #     path = app.root_path + '/data/StreamingHistory1.json'
    #     spotify_data = sg.read_data(path)
    #     long_listens = sg.get_long_listens(spotify_data)
    #     chart_json = sg.render_chart(long_listens)
    #     return render_template("index.html", data=json.dumps(chart_json))

    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # return redirect(url_for('uploaded_file',
                #                         filename=filename))
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                spotify_data = sg.read_data(path)
                long_listens = sg.get_long_listens(spotify_data)
                chart_json = sg.render_chart(long_listens)
                return render_template("index.html", data=json.dumps(chart_json))

        else:
            return render_template("index.html", data=json.dumps(dict()))

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename)

    
    @app.route('/data/spotify_top_artists.html')
    def show_network():
        path  = app.root_path + '/data/spotify_top_artists.html'
        cid = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_ID')
        secret = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_SECRET')
        uri = os.environ.get('SPOTIFY_UNWRAPPED_CALLBACK')
        short_term_top, med_term_top, long_term_top = gn.get_user_top_artists(cid, secret, uri)
        gn.genre_network_graph(short_term_top, path)
        return flask.send_file(path)
        
    @app.route('/data/style.css')
    def return_css():
        path  = app.root_path + '/data/style.css'
        flask.send_file(path)



    return app
