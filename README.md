# Spotify Unwrapped

Welcome to Spotify (Un)wrapped...
...where you can view your Spotify analytics any time of year! Explore our interactive genre network graph, or upload your Spotify streaming history to view your stream history graph. Happy exploring!

To run:
- Clone the repository: `git clone https://github.com/data-challengers/final-project.git`
- Install packages: `pip install -r requirements.txt`
- Set environment variables (`export VAR_NAME=value` on Unix systems, `set VAR_NAME=value`) on Windows
  - `SPOTIFY_UNWRAPPED_CLIENT_ID`, `SPOTIFY_UNWRAPPED_CLIENT_SECRET`, and `SPOTIFY_UNWRAPPED_CALLBACK`: obtained by registering a [Spotify developer application](https://developer.spotify.com/dashboard/applications)
  - `FLASK_APP=unwrapped`
- `cd app/`
- `flask run`
