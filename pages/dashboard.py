import dash
import datetime
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import dcc, html
import calendar
import numpy as np
import json


dash.register_page(__name__, path='/')  # homepage
conn = sqlite3.connect('employees.db')
df = pd.read_sql_query(
    "SELECT m.employee_id,m.employee_name, m.business_unit, status,date FROM master as m INNER JOIN attendance UsING (employee_id)",
    conn)


df2 = pd.read_sql_query("SELECT employee_id,shift_date, rto_days FROM rto",conn)
m = []
original_list=[]
for idx,i in enumerate(df2['rto_days']):
    for k in i.split(','):
        m.append(str(df2['shift_date'][idx])+"_"+str(k))
    x = m.copy()
    m.clear()
    original_list.append({df2['employee_id'][idx]:x})
    
new_list = {}
for item in original_list:
    for key, value in item.items():
        if key in new_list:
            new_list[key] += value
        else:
            new_list[key] = value





# important functions:
# function_1.storing the value of date.today in a variable today
def slicer(no_of_days):
    today = str(df['date'].max()).split('-')
    payday = datetime.date(int(today[0]), int(today[1]), int(today[2]))
    chqday = datetime.timedelta(no_of_days)
    n_payday = payday - chqday
    # take slice with final week of data
    sliced_df = df[(df['date'] >= str(n_payday)) &
                   (df['date'] <= str(payday))]

    new_col = sliced_df['date'].unique()
    new_col.sort()
    sliced_df = sliced_df.pivot_table(index=['employee_id', "employee_name", 'business_unit'], columns=["date"],
                                      values='status')
    sliced_df = sliced_df.reset_index().rename_axis(None, axis=1)
    for i in new_col:
        dys = datetime.datetime.strptime(i, '%Y-%m-%d').weekday()
        sliced_df.rename(columns={i:  i+"_"+calendar.day_name[dys]}, inplace=True)

    return sliced_df



#1. Element business unit dropdown:
bu_dropdown_dashboard = dcc.Dropdown(id='business-unit-dropdown-dashboard',
                       options=[{'label': i, 'value': i} for i in df['business_unit'].unique()],
                       optionHeight=40,
                       multi=False,
                       searchable=True,
                       search_value='',
                       clearable=True,
                       style={'width': "45%"},
                       placeholder='Select Business Unit')

#2. Element date range picker:date range
date_range_dashboard = dcc.DatePickerRange(
    id="my-date-picker-range-dashboard",
    start_date=df["date"].min(),
    end_date=df["date"].max(),
    min_date_allowed=df["date"].min(),
    max_date_allowed=df["date"].max()
)



#3. Element dash table:
data_for_table = slicer(9)
dashboard_table = dash_table.DataTable(
    id='datatable-interactivity-dashboard',
    columns=[
        {'id':col , 'name':col , 'presentation': 'dropdown'}
        for col in data_for_table.columns
         
    ],
    data=data_for_table.to_dict('records'),
    page_current=0,  # page number that user is on
    page_size=10,
    row_selectable="multi", 
    editable=True,
    dropdown={
            f'{col}': {
                'options': [
                    {'label': str(i), 'value': i}
                    for i in np.array([0,1])
                ]
            }for col in data_for_table.columns[3:]} ,  
     
    style_data_conditional=[
           {
            'if': {'filter_query':f'{{employee_id}} = {i}' , 'column_id': new_list[i] },
            'backgroundColor': 'lightgreen',
            'color': 'black',
        } for i in new_list
    ]
    
    
    
              
              
    
)







layout = html.Div([
    
    dbc.Row([
        html.H1("DASHBOARD", style={'fontSize': 30, 'textAlign': 'center'})
    ]),
    html.Hr(),
    
    dbc.Row([
        dbc.Col(width =2),
        dbc.Col([bu_dropdown_dashboard],width=6),
        dbc.Col([date_range_dashboard], width=4, id='calender-for-date-range')
    ]), 
    
    
    dbc.Row([
        dbc.Col(width =2),
        dbc.Col([dashboard_table, html.Div(id='datatable-interactivity-container')],width=9)
    ]), 
    
    dbc.Row([
        dbc.Col(width = 10),
        dbc.Col(
            [html.Button('Submit', id='attandance-submit-btn', n_clicks=0), html.Div(id='container-button-timestamp')],
            width=2, )
 ] ) 
])