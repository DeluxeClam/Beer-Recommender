# Let's make a Dash app for beers.

import pandas as pd
import numpy as np
from math import ceil

from dash import Dash, dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px

# Import data
gabs_year = 2024

data_beers = pd.read_csv(f"Data/GABS_{gabs_year}_festival_beers.csv")
data_2d_embed = pd.read_csv(f"Data/GABS_{gabs_year}_embeddings.csv")
data_similarity = pd.read_csv(f"Data/GABS_{gabs_year}_similarity_matrix.csv").set_index("num")

# Import style
external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Lato:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = f"The GABS {gabs_year} Beer Recommender"

# Helper functions
def get_recs(ind, num_recs):
    # Get index of recs
    rec_inds = np.argsort(data_similarity.to_numpy()[int(ind)])[-num_recs:][::-1]
    # Get recs
    return data_beers.set_index('num').iloc[rec_inds].reset_index()

def get_beer_ind(num):
    df_entry = data_beers.query(f"num=={int(num)}")
    return data_beers.index.get_loc(df_entry.index[0])

# Setup app components
app_desc = dcc.Markdown(id="app_desc",
                        children="If you can filter down to one beer, you get a surprise."
                        )
beer_data_table = dash_table.DataTable(id="beers_table",
                                       data=data_beers.to_dict('records'),
                                       page_size=10,
                                       fill_width=False,
                                       style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                       style_cell={'maxWidth':'700px'}
                                       )
beer_recs_table = dash_table.DataTable(id="recs_table",
                                       data=data_beers.query("abv==100").to_dict('records'),
                                       page_size=10,
                                       fill_width=False,
                                       style_data={'whiteSpace': 'normal', 'height': 'auto'},
                                       style_cell={'maxWidth':'700px'}
                                       )
num_dropdown = dcc.Dropdown(id="number_dropdown",
                            options=sorted(data_beers['num'].unique()),
                            multi=True
                            )
section_dropdown = dcc.Dropdown(id="section_dropdown",
                                options=sorted(data_beers['section'].unique()),
                                multi=True
                                )
state_dropdown = dcc.Dropdown(id="state_dropdown",
                              options=sorted(data_beers['state'].unique()),
                              multi=True
                              )
style_dropdown = dcc.Dropdown(id="style_dropdown",
                              options=sorted(data_beers['style'].unique()),
                              multi=True
                              )
abv_slider = dcc.RangeSlider(id="abv_slider",
                             min=0,
                             max=ceil(max(data_beers['abv'])) + 1,
                             step=1,
                             value=[1, 13]
                             )
beer_button = html.Button(id='beer_button',
                     children='🍻',
                     n_clicks=0,
                     style={'font-size':54}
                     )
reset_button = html.Button(id='reset_button',
                     children='🫗',
                     n_clicks=0,
                     style={'font-size':54}
                     )
beer_map = dcc.Graph(id="beer_map",
                     figure=px.scatter(data_2d_embed,
                                       x="0",
                                       y="1",
                                       color="Abv",
                                       hover_data={"0":False, "1":False, "Beer":True, "Number":True,
                                                   "Section":True, "Style":True, "Brewery":True
                                                   },
                                        title="GABS 2024 Beer Map",
                                        height=800,
                                        width=1000,
                                        labels={"0":"Sideways beeriness", "1":"Beeryness, but upwards"}
                                        ),
                     responsive=True,
                     style={'width': '100%', 'height': '60vh'}
                    )


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="🍺 Beer Recommender 🍺",
                        className="header-title"
                        ),
                html.P(
                    children=(
                        "Did you like one of the GABS beers"
                        " and want more like that but not that one exactly?"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        dbc.Container([
            html.Br(),
            app_desc,
            html.Br(),
            dbc.Row([
                dbc.Col(children=["Select number...", num_dropdown], width=2),
                dbc.Col(children=["Select section...", section_dropdown], width=2),
                dbc.Col(children=["Select state...", state_dropdown], width=2),
                dbc.Col(children=["Select style...", style_dropdown], width=4),
                dbc.Col(children=beer_button, width=1),
                dbc.Col(children=reset_button, width=1),
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "Select ABV%",
                    html.Br(),
                    abv_slider
                ], width=12)  
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "The Beers",
                    html.Br(),
                    beer_data_table
                ], width=12)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "The Recs",
                    html.Br(),
                    beer_recs_table
                ], width=12)
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    "The Beer Map",
                    html.Br(),
                    beer_map
                ], width=12)
            ])
        ])        
    ]
)

@app.callback(
    Output(component_id="beers_table", component_property="data"),
    Output(component_id="beer_map", component_property="figure"),
    Output(component_id="recs_table", component_property="data"),
    Input(component_id="beer_button", component_property='n_clicks'),
    State(component_id="number_dropdown", component_property='value'),
    State(component_id="section_dropdown", component_property='value'),
    State(component_id="state_dropdown", component_property='value'),
    State(component_id="style_dropdown", component_property='value'),
    State(component_id="abv_slider", component_property='value'),
    State(component_id="beer_map", component_property="figure"),
    State(component_id="recs_table", component_property="data")
)
def update_app(n_clicks, number, section, state, style, abv, beer_map, recs):
    
    data_manip = data_beers
    
    if n_clicks >= 0:

        # Update data table
        slice_conditions = [[True for _ in range(data_beers.shape[0])]]
        
        if number:
            slice_conditions.append(data_beers['num'].isin(number))
        if section:
            slice_conditions.append(data_beers['section'].isin(section))
        if state:
            slice_conditions.append(data_beers['state'].isin(state))
        if style:
            slice_conditions.append(data_beers['style'].isin(style))
        if abv:
            slice_conditions.append((data_beers['abv'] >= abv[0]) & (data_beers['abv'] <= abv[1]))
        
        data_manip = data_beers[np.bitwise_and.reduce(slice_conditions)]

        # Update beer map
        if data_manip.shape[0] > 0:
            data = data_2d_embed[data_2d_embed['Number'].isin(data_manip['num'])]
            xmin = min(data['0']) - 0.1
            xmax = max(data['0']) + 0.1
            ymin = min(data['1']) - 0.1
            ymax = max(data['1']) + 0.1

            beer_map = px.scatter(data_2d_embed,
                                       x="0",
                                       y="1",
                                       color="Abv",
                                       hover_data={"0":False, "1":False, "Beer":True, "Number":True,
                                                   "Section":True, "Style":True, "Brewery":True
                                                   },
                                        title="GABS 2024 Beer Map",
                                        height=800,
                                        width=1000,
                                        range_x=[xmin, xmax],
                                        range_y=[ymin, ymax]
                            )
        else:
            beer_map = px.scatter(data_2d_embed,
                                       x="0",
                                       y="1",
                                       color="Abv",
                                       hover_data={"0":False, "1":False, "Beer":True, "Number":True,
                                                   "Section":True, "Style":True, "Brewery":True
                                                   },
                                        title="GABS 2024 Beer Map",
                                        height=800,
                                        width=1000
                            )
        
        # Update rec table
        if data_manip.shape[0] == 1:
            num = data_manip['num'].iloc[0]
            recs = get_recs(get_beer_ind(num), 5).to_dict('records')

    return data_manip.to_dict('records'), beer_map, recs

@app.callback(
    Output(component_id="beer_button", component_property='n_clicks'),
    Output(component_id="number_dropdown", component_property='value'),
    Output(component_id="section_dropdown", component_property='value'),
    Output(component_id="state_dropdown", component_property='value'),
    Output(component_id="style_dropdown", component_property='value'),
    Output(component_id="abv_slider", component_property='value'),
    Input(component_id="reset_button", component_property="n_clicks")
)
def reset_app(n_clicks):
    return (0, [], [], [], [], [1, 13])

if __name__ == "__main__":
    app.run_server(debug=True)