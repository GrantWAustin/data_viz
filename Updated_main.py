import pandas as pd
import numpy as np
import json
import plotly.express as px

from dash import Dash, dcc, html, Input, Output

# load the data into a pandas dataframe
df = pd.read_csv('Motor_Vehicle_Collisions_-_Crashes.csv') #There may be a DtypeWarning for Column(3), ZIP CODE. Disregard for now, taken care of a few lines down.

#Display the first five rows of the dataframe
#print(df.head())

#Convert ZIP codes to strings, remove any decimal points, replace the string "nan" with NaN value
df['ZIP CODE'] = df['ZIP CODE'].astype(str)
df['ZIP CODE'] = df['ZIP CODE'].str.split('.').str[0]
df['ZIP CODE'] = df['ZIP CODE'].replace('nan', np.nan)

#Sum up and print counts of null values in each column
#missing_values = df.isnull().sum()
#print(missing_values)

#Drop null ZIP codes and check again
df = df.dropna(subset=['ZIP CODE'])

#missing_values2 = df.isnull().sum()
#print(missing_values2)

#Check the head again to ensure all ZIPs are displayed correctly and the nulls are removed
print(df.head())

#create the dash app
app = Dash(__name__)

#create a copy of the dataframe
dff = df.copy()

#group by       zip code (MAP)      and sum (REDUCE)
dff = dff.groupby('ZIP CODE').agg({'NUMBER OF PERSONS INJURED': 'sum', 
                                   'NUMBER OF PERSONS KILLED': 'sum', 
                                   'NUMBER OF PEDESTRIANS INJURED': 'sum', 
                                   'NUMBER OF PEDESTRIANS KILLED': 'sum', 
                                   'NUMBER OF CYCLIST INJURED': 'sum', 
                                   'NUMBER OF CYCLIST KILLED': 'sum', 
                                   'NUMBER OF MOTORIST INJURED': 'sum', 
                                   'NUMBER OF MOTORIST KILLED': 'sum',
                                   'CRASH DATE': 'count',
                                   }).reset_index() 

dff = dff.rename(columns={'CRASH DATE': 'TOTAL CRASHES'})

#Calculate average metrics
dff['AVG PERSONS INJURED PER CRASH'] = dff['NUMBER OF PERSONS INJURED'] / dff['TOTAL CRASHES']
dff['AVG PERSONS KILLED PER CRASH'] = dff['NUMBER OF PERSONS KILLED'] / dff['TOTAL CRASHES']

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
                    {'label': 'TOTAL CRASHES', 'value': 'TOTAL CRASHES'},
                    {'label': 'PERSONS INJURED', 'value': 'NUMBER OF PERSONS INJURED'},
                    {'label': 'PERSONS KILLED', 'value': 'NUMBER OF PERSONS KILLED'},
                    {'label': 'PEDESTRIANS INJURED', 'value': 'NUMBER OF PEDESTRIANS INJURED'},
                    {'label': 'PEDESTRIANS KILLED', 'value': 'NUMBER OF PEDESTRIANS KILLED'},
                    {'label': 'CYCLIST INJURED', 'value': 'NUMBER OF CYCLIST INJURED'},
                    {'label': 'CYCLIST KILLED', 'value': 'NUMBER OF CYCLIST KILLED'},
                    {'label': 'MOTORIST INJURED', 'value': 'NUMBER OF MOTORIST INJURED'},
                    {'label': 'MOTORIST KILLED', 'value': 'NUMBER OF MOTORIST KILLED'},
                    {'label': 'AVG PERSONS INJURED PER CRASH', 'value': 'AVG PERSONS INJURED PER CRASH'},
                    {'label': 'AVG PERSONS KILLED PER CRASH', 'value': 'AVG PERSONS KILLED PER CRASH'},
                 ], 
                 multi=False,
                 value = 'TOTAL CRASHES'),
    dcc.Graph(id='graph-content')
])

#callback function
@app.callback(
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='dropdown-selection', component_property='value')
)
def update_graph(selected_value):
    max_value = dff[selected_value].max()  #Get the maximum value for the selected column
    #print(f"Max value for {selected_value}: {max_value}")  #Debugging statement
    
    #plot the map
    fig = px.choropleth(    dff,                                 # data frame
                            geojson=ny_zips_json,                # geojson file
                            locations='ZIP CODE',                # column in data frame for mapping
                            featureidkey="properties.ZCTA5CE10", # key in geojson file for mapping
                            color=selected_value,                # column in data frame for color
                            color_continuous_scale="reds",       # color scale
                            projection="mercator",               # projection
                            range_color=(0, max_value),          # Set the range for the color scale
                            ) # change color to column name
    
    #update the layout
    fig.update_geos(fitbounds="locations", visible=False) # fitbounds="locations", specified in px.choropleth
    fig.update_coloraxes(colorbar_tickformat=',')  #Add this line to prevent shortening of numbers
    
    #Customize hover template and update the layout dynamically based on the selected value
    if "AVG" in selected_value:
        hover_text = f'<b>ZIP Code:</b> %{{location}}<br><b>{selected_value}:</b> %{{z:.3f}}<extra></extra>'
    else:
        hover_text = f'<b>ZIP Code:</b> %{{location}}<br><b>{selected_value}:</b> %{{z:,.0f}}<extra></extra>'
    
    fig.update_traces(hovertemplate=hover_text)

    return fig

#Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
