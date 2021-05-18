import os
import flask
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pyvis.network import Network
import networkx as nx
import unwrapped.genre_network as gn
import unwrapped.streamgraph as sg
from flask import Flask, render_template

import json

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,
    static_folder='data')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'unwrapped.sqlite'),
    )

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

    @app.route("/")
    def index():
        path = app.root_path + '/data/StreamingHistory1.json'
        spotify_data = sg.read_data(path)
        long_listens = sg.get_long_listens(spotify_data)
        chart_json = sg.render_chart(long_listens)
        # chart_json = {
        # "$schema": 'https://vega.github.io/schema/vega-lite/v5.json',
        # "description": 'A simple bar chart with embedded data.',
        # "data": {
        #   "values": [
        #     {"a": 'A', "b": 28},
        #     {"a": 'B', "b": 55},
        #     {"a": 'C', "b": 43},
        #     {"a": 'D', "b": 91},
        #     {"a": 'E', "b": 81},
        #     {"a": 'F', "b": 53},
        #     {"a": 'G', "b": 19},
        #     {"a": 'H', "b": 87},
        #     {"a": 'I', "b": 52}
        #   ]
        # }
        # }
        return render_template("index.html",
        data=json.dumps(chart_json))

    @app.route('/data/spotify_top_artists.html')
    def show_network():
        path  = app.root_path + '/data/spotify_top_artists.html'
        cid = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_ID')
        secret = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_SECRET')
        uri = os.environ.get('SPOTIFY_UNWRAPPED_CALLBACK')
        short_term_top, med_term_top, long_term_top = gn.get_user_top_artists(cid, secret, uri)
        gn.genre_network_graph(short_term_top, path)
        return flask.send_file(path)

    # @app.route('/data/streamgraph.json')
    # def show_streamgraph():
    return app
