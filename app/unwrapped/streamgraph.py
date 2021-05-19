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

    # keep top 20 listened artists in a period
    #long_listens = long_listens.sort_values('seconds_played').groupby(['endTime']).tail(5)
    long_listens = long_listens.sort_values('seconds_played').tail(20)

    return long_listens

def render_chart(long_listens):
    alt.data_transformers.disable_max_rows()
    
    selection = alt.selection_multi(fields=['artistName'], bind='legend')


    chart = alt.Chart(long_listens).mark_area().encode(
        alt.X('endTime'),
        alt.Y('seconds_played', stack='center', axis=None),
        alt.Color('artistName',
            scale=alt.Scale(scheme='category20b')
        ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    ).interactive()

    return (chart).to_dict()
