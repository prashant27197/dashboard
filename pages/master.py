import dash
import datetime
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import dcc, html
import calendar
import numpy as np


dash.register_page(__name__, path='/master')  # homepage

#1. Upload Button:
# upload section
upload_file = dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=True
)





layout = html.Div([
    dbc.Row([html.H1("FILE UPLOAD", style={'fontSize': 30, 'textAlign': 'center'})]),
    html.Hr(),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col([upload_file], width=8, id='output-data-upload'),
    ]),
])