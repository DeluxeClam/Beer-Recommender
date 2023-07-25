# Let's make a Dash app for beers.

import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

data_beers = pd.read_csv("Data/GABS_2023_Festival_Beers.csv")
data_embed = pd.read_csv("Data/GABS_embedding.csv")

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
app.title = "The GABS 2023 Beer Recommender"


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
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data_beers["Section"],
                        "y": data_beers["Anticipation"],
                        "type": "box",
                    },
                ],
                "layout": {"title": "Beer Ratings by Section"},
            },
        ),
        dcc.Graph(
            figure = px.scatter(data_embed,
                                x="0",
                                y="1",
                                color="Style",
                                hover_data=["Beer", "Section", "Number"]
                                )
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)