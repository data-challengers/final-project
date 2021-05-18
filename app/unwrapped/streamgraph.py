import pandas as pd
import datetime as dt
import altair as alt

def read_data(raw_data):
    # read in json (converts to df)
    spotify_data = pd.read_json(raw_data)

    # set df as datetime
    spotify_data['endTime'] = pd.to_datetime(spotify_data['endTime'])

    # convert from milliseconds to seconds (for readibility)
    spotify_data['seconds_played'] = spotify_data['msPlayed']/1000
    return spotify_data

def get_long_listens(spotify_data):
    long_listens = spotify_data[spotify_data['seconds_played'] >= 120]

    # floor endtime by date
    long_listens['endTime'] = long_listens['endTime'].dt.round('D') 

    # floor endtime by month
    long_listens['endTime'] = long_listens['endTime'].dt.to_period('M').dt.to_timestamp()

    # group by endtime and artist, take sum of seconds played
    long_listens = long_listens[['endTime', 'artistName', 'seconds_played']].groupby(['endTime', 'artistName'], as_index = False)['seconds_played'].agg('sum')

    # keep top 5 listened artists in a period
    long_listens = long_listens.sort_values('seconds_played').groupby(['endTime']).tail(5)
    return long_listens

def render_chart(long_listens):
    alt.data_transformers.disable_max_rows()

    chart = alt.Chart(long_listens).mark_area().encode(
        x = 'endTime',
        y = 'seconds_played',
        color = 'artistName'
    ).properties(
        height = 'container',
        width = 'container',
    )


    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=7
    ).encode(
        text='artistName'
    )

    return (text + chart).to_dict()
