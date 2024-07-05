import json
import plotly.express as px
import pandas as pd
import numpy as np

from dash import Dash, dcc, html, Input, Output

#create the dash app
app = Dash(__name__)

#load the data into a pandas dataframe
# CRASH DATE,CRASH TIME,BOROUGH,ZIP CODE,LATITUDE,LONGITUDE,LOCATION,ON STREET NAME,CROSS STREET NAME,OFF STREET NAME,
# NUMBER OF PERSONS INJURED,NUMBER OF PERSONS KILLED,NUMBER OF PEDESTRIANS INJURED,NUMBER OF PEDESTRIANS KILLED,NUMBER OF CYCLIST INJURED,NUMBER OF CYCLIST KILLED,NUMBER OF MOTORIST INJURED,NUMBER OF MOTORIST KILLED,
# CONTRIBUTING FACTOR VEHICLE 1,CONTRIBUTING FACTOR VEHICLE 2,CONTRIBUTING FACTOR VEHICLE 3,CONTRIBUTING FACTOR VEHICLE 4,CONTRIBUTING FACTOR VEHICLE 5,
# COLLISION_ID,VEHICLE TYPE CODE 1,VEHICLE TYPE CODE 2,VEHICLE TYPE CODE 3,VEHICLE TYPE CODE 4,VEHICLE TYPE CODE 5
df = pd.read_csv('Motor_Vehicle_Collisions_-_Crashes.csv')

#create a copy of the dataframe
dff = df.copy()

#filter the data to only include usable zip codes
dff['ZIP CODE'] = dff['ZIP CODE'].str.replace(' ', '') #remove spaces
dff = dff.dropna(subset=['ZIP CODE']) #drop rows with no zip code

#group by       zip code (MAP)      and sum (REDUCE)
dff = dff.groupby('ZIP CODE').agg({'NUMBER OF PERSONS INJURED': 'sum', 
                                   'NUMBER OF PERSONS KILLED': 'sum', 
                                   'NUMBER OF PEDESTRIANS INJURED': 'sum', 
                                   'NUMBER OF PEDESTRIANS KILLED': 'sum', 
                                   'NUMBER OF CYCLIST INJURED': 'sum', 
                                   'NUMBER OF CYCLIST KILLED': 'sum', 
                                   'NUMBER OF MOTORIST INJURED': 'sum', 
                                   'NUMBER OF MOTORIST KILLED': 'sum',
                                   }).reset_index() 

#print dff
print(dff)

#load the geojson file
ny_zips_json = json.load(open('ny_new_york_zip_codes_geo.min.json'))

#find the zip codes that are not in the geojson file
for i in range(len(dff)):
    zip_code = dff['ZIP CODE'].iloc[i]
    if zip_code not in [x['properties']['ZCTA5CE10'] for x in ny_zips_json['features']]:
        print(f"Data for: {zip_code} but no GEOJson")

#layout of the app
app.layout = html.Div([
    html.H1(children='New York City Motor Vehicle Collisions', style={'textAlign':'center'}),
    dcc.Dropdown(id='dropdown-selection', 
                 options= [
                    {'label': 'PERSONS INJURED', 'value': 'NUMBER OF PERSONS INJURED'},
                    {'label': 'PERSONS KILLED', 'value': 'NUMBER OF PERSONS KILLED'},
                    {'label': 'PEDESTRIANS INJURED', 'value': 'NUMBER OF PEDESTRIANS INJURED'},
                    {'label': 'PEDESTRIANS KILLED', 'value': 'NUMBER OF PEDESTRIANS KILLED'},
                    {'label': 'CYCLIST INJURED', 'value': 'NUMBER OF CYCLIST INJURED'},
                    {'label': 'CYCLIST KILLED', 'value': 'NUMBER OF CYCLIST KILLED'},
                    {'label': 'MOTORIST INJURED', 'value': 'NUMBER OF MOTORIST INJURED'},
                    {'label': 'MOTORIST KILLED', 'value': 'NUMBER OF MOTORIST KILLED'},
                 ], 
                 multi=False,
                 value = 'NUMBER OF PERSONS INJURED'),
    dcc.Graph(id='graph-content')
])

#callback function
@app.callback(
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='dropdown-selection', component_property='value')
)
def update_graph(selected_value):
    #plot the map
    fig = px.choropleth(    dff,                                 # data frame
                            geojson=ny_zips_json,                # geojson file
                            locations='ZIP CODE',                # column in data frame for mapping
                            featureidkey="properties.ZCTA5CE10", # key in geojson file for mapping
                            color=selected_value,                # column in data frame for color
                            color_continuous_scale="reds",       # color scale
                            projection="mercator",               # projection
                            ) # change color to column name
    
    #update the layout
    fig.update_geos(fitbounds="locations", visible=False) # fitbounds="locations", specified in px.choropleth
    #fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}) # remove margin

    return fig

#show the plotted map
#fig.show()
app.run(debug=True, port=8050)