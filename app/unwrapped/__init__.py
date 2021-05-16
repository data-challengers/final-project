import os
import flask
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pyvis.network import Network
import networkx as nx

from flask import Flask, render_template


def get_user_top_artists(cid, secret, uri):
    """
    :param: cid - Spotify app client identification 
    :param: secret - App-specific client secret
    :param: uri - App-specific uri (must be registered on Spotify Developer Dashboard)
    This function will run upon app load.
    Prompts the user for Spotify login and gets top artist lists.
    
    References: 
    https://github.com/plamere/spotipy/blob/master/examples/my_top_artists.py
    https://developer.spotify.com/documentation/web-api/reference/#endpoint-get-users-top-artists-and-tracks
    """
    scope = "user-top-read"
    ranges = ['short_term', 'medium_term', 'long_term']

    # Access indiv spotify account (prompts sign in on localhost uri)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=cid, client_secret=secret, redirect_uri=uri))

    # Get top artists
    top_artists = {}
    for sp_range in ['short_term', 'medium_term', 'long_term']:
        results = sp.current_user_top_artists(time_range=sp_range, limit=25)
        top_artists[sp_range] = results['items']
    
    # Top artists lists ranked by user-specific popularity
    short_term_top = pd.DataFrame(top_artists['short_term'])
    med_term_top = pd.DataFrame(top_artists['medium_term'])
    long_term_top = pd.DataFrame(top_artists['long_term'])
    return short_term_top, med_term_top, long_term_top

def set_pop_color(pop):
    color = ""
    if pop >= 95:
        color = "#DC267F"
    elif pop >= 90: 
        color = "#FE6100"
    elif pop >= 75:
        color = "#FFB000"
    elif pop >= 50:
        color = "#648FFF"
    else:
        color = "#785EF0"
    return color

def create_genres_dict(df):
    # Create genres dictionary
    top_genres = {}
    for index, row in df.iterrows():
        for genre in row['genres']:
            if genre in top_genres:
                top_genres[genre].append(row['name'])
            else:
                top_genres[genre] = [row['name']]
    return top_genres

def genre_network_graph(df, path):
    """
    This method takes in a dataframe of top artists and creates an undirected network graph of artist genres.
    Edge weight increases based on artist genre overlap. 
    Color is mapped to the Spotify-created artist popularity score (out of 100)
    Creates an html output containing the network graph.
    
    :param: df - dataframe of user top artists
    """
    # Create top genres dict
    top_genres = create_genres_dict(df)
    # Map artist names to node ids
    artist_dict = {}
    # Initialize networkx graph
    nx_graph=nx.empty_graph(create_using=nx.Graph())

    # create artist nodes, sized by order of user preference
    for i in df.index:
        artist_name = df.iloc[i]['name']
        # set node color based on overall popularity
        node_color = set_pop_color(df.iloc[i]['popularity'])
        # set node size based on user-specific ranking of popularity
        node_size = 30-i
        if i == 0:
            node_size = 35
        elif node_size < 10:
            node_size = 10
        node_title = str(i+1) + ", " + artist_name + ": " + str(df.iloc[i]['genres'])
        nx_graph.add_node(i, label=artist_name, size=node_size, title=node_title, color=node_color)
        artist_dict[artist_name] = i

    # Create edges connecting artist of the same genres
    # loop through genres dict
    for genre, artists in top_genres.items():
        # if genre has more than one artist
        if len(artists) >= 2:
            # loop through artists and create genre edges
            for i in range(len(artists)):
                for j in range(i+1, len(artists)):
                    source = artist_dict[artists[i]]
                    dest = artist_dict[artists[j]]
                    # check if an edge already exists between the two artists
                    if nx_graph.has_edge(source, dest):
                        # increase thickness of edge
                        prev_weight = nx_graph[source][dest]['width']
                        prev_title = nx_graph[source][dest]['title']
                        nx_graph[source][dest]['width'] = prev_weight+2
                        nx_graph[source][dest]['title'] = prev_title + ", " + genre
                    else:
                        nx_graph.add_edge(source, dest, title=genre, width=1, color='#000000')



    nt = Network("500px", "800px")
    nt.from_nx(nx_graph)
    nt.save_graph(path)

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
        return render_template("index.html"
        #, message="Hello Flask!"
        );   

    @app.route('/data/spotify_top_artists.html')
    def show_network():
        path  = app.root_path + '/data/spotify_top_artists.html'
        cid = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_ID')
        secret = os.environ.get('SPOTIFY_UNWRAPPED_CLIENT_SECRET')
        uri = os.environ.get('SPOTIFY_UNWRAPPED_CALLBACK')
        short_term_top, med_term_top, long_term_top = get_user_top_artists(cid, secret, uri)
        genre_network_graph(short_term_top, path)
        return flask.send_file(path)


    return app
