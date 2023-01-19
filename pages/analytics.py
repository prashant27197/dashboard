import dash
import datetime
import pandas as pd
import sqlite3
from datetime import date
import dash_bootstrap_components as dbc
from dash import dash_table
from dash import dcc, html
import calendar
import numpy as np


dash.register_page(__name__, path='/analytics')  # homepage
conn = sqlite3.connect('employees.db')
#for setting the in the calenders:
set_date = pd.read_sql_query("SELECT date from attendance ",conn)
set_business = pd.read_sql_query("SELECT business_unit FROM master",conn)

# for converting the dates of claenders:
def calendar_date_to_string(date_value):
   date_value = date.fromisoformat(str(date_value)).strftime('%Y,%m,%d').split(',')
   date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))
   return date_value

#day name returner for perticular date:
def day_name_returner(date):
    dys = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
    dys =calendar.day_name[dys]
    return dys

#function for rto table1
def rto_status_finder(start_date,end_date):
    conn = sqlite3.connect('employees.db')
    df = pd.read_sql_query(
    "SELECT r.employee_id,b.business_unit, r.rto_days, a.date , a.status  FROM rto as r INNER JOIN attendance as a USING(employee_id) INNER Join master as b USING(employee_id) ORDER BY date",
    conn)
    from_date = calendar_date_to_string(start_date)
    to_date = calendar_date_to_string(end_date)
    df = df[(df['date'] >= str(from_date)) &
                   (df['date'] <= str(to_date))]
    df.drop_duplicates(inplace=True)
    df['date_day']=df['date'].apply(day_name_returner)
    data_rto_analytics = df[df.apply(lambda x: x.date_day in x.rto_days, axis=1)]
    data_rto_analytics.reset_index(inplace=True)
    data_rto_analytics = data_rto_analytics[['business_unit','status']]
    data_rto_analytics['Total Attendance'] = 1  
    result = data_rto_analytics.groupby('business_unit').sum().reset_index().rename_axis(None, axis=1).rename(columns={'status': 'RTO Attendance'})
    return result


#function for export table:
def data_filter_for_export(no_of_days):
   conn = sqlite3.connect('employees.db')
   cur = conn.cursor()
   df = pd.read_sql_query("SELECT m.employee_id,m.employee_name, m.business_unit, date,status FROM master as m INNER JOIN attendance UsING (employee_id)",conn)
   # storing the value of date.today in a variable today
   today = str(df['date'].max()).split('-')
   payday = datetime.date(int(today[0]), int(today[1]), int(today[2]))
   chqday = datetime.timedelta(no_of_days)
   n_payday = payday - chqday
   sliced_df = df[(df['date'] >= str(n_payday)) &
                  (df['date'] <= str(payday))]
   
   return sliced_df


#date range for rto table:
date_range_analytics1 = dcc.DatePickerRange(
    id="my-date-picker-range-analytics",
    start_date=set_date["date"].min(),
    end_date=set_date["date"].max(),
    min_date_allowed=set_date["date"].min(),
    max_date_allowed=set_date["date"].max()
)

#rto table:
das_table2=rto_status_finder(set_date["date"].min(),set_date["date"].max())
table1 = dash_table.DataTable(
    id='datatable-daterange-rto-interactivity-analytics',
    columns=[
        {'id': i, 'name': i, 'presentation': 'dropdown'}
        for i in das_table2.columns
    ],
    data=das_table2.to_dict('records'),
    page_current=0,  # page number that user is on
    page_size=10,
    export_format="csv")
    


# 2 RTO attendance business unitwise analytics 
row3_BU = dcc.Dropdown(id='business-unit-dropdown-two-analytics',
                       options=[{'label': i, 'value': i} for i in set_business['business_unit'].unique()],
                       optionHeight=40,
                       multi=False,
                       value="Data Science",
                       searchable=True,
                       search_value='',
                       clearable=True,
                       style={'width': "45%"},
                       placeholder='Select Business Unit')




def rto_status_bunits_finder(start_date,end_date,business_unit):
    conn = sqlite3.connect('employees.db')
    df = pd.read_sql_query(
    "SELECT r.employee_id,b.employee_name, b.business_unit, r.rto_days, a.date , a.status  FROM rto as r INNER JOIN attendance as a USING(employee_id) INNER Join master as b USING(employee_id) ORDER BY date",
    conn)
    from_date = calendar_date_to_string(start_date)
    to_date = calendar_date_to_string(end_date)
    df = df[(df['date'] >= str(from_date)) &
                   (df['date'] <= str(to_date))&(df['business_unit'] == str(business_unit))]
    df.drop_duplicates(inplace=True)
    df['date_day']=df['date'].apply(day_name_returner)
    data_rto_analytics = df[df.apply(lambda x: x.date_day in x.rto_days, axis=1)]
    data_rto_analytics.reset_index(inplace=True)
    data_rto_analytics = data_rto_analytics[['employee_name','status']]
    data_rto_analytics['Total Attendance'] = 1  
    result = data_rto_analytics.groupby('employee_name').sum().reset_index().rename_axis(None, axis=1).rename(columns={'status': 'RTO Attendance'})
    return result


#date range for rto table and business unit:
date_range_analytics2 = dcc.DatePickerRange(
    id="my-date-picker-range-two-analytics",
    start_date=set_date["date"].min(),
    end_date=set_date["date"].max(),
    min_date_allowed=set_date["date"].min(),
    max_date_allowed=set_date["date"].max()
)

#rto table:
das_table3=rto_status_bunits_finder(set_date["date"].min(),set_date["date"].max(),str(set_business['business_unit'].iloc[0]))
table3 = dash_table.DataTable(
    id='datatable-daterange-bunits-rto-interactivity-analytics',
    columns=[
        {'id': i, 'name': i, 'presentation': 'dropdown'}
        for i in das_table3.columns
    ],
    data=das_table3.to_dict('records'),
    page_current=0,  # page number that user is on
    page_size=10,
    export_format="csv")


#dropdwon for exporting the data:
export_dropdown = dcc.Dropdown(id='exportd-data-dropdown-analytics',
                       options=[{'label':'6 month', 'value': 182},
                                {'label':'3 month', 'value': 91},
                                {'label':'1 month', 'value': 29},
                                {'label':'1 week', 'value': 6}],
                       optionHeight=40,
                       multi=False,
                       value=0,
                       searchable=True,
                       search_value='',
                       clearable=True,
                       style={'width': "45%"},
                       placeholder='Select to Export')

#dropdown for downloding the data:

export_table_data = data_filter_for_export(0)
table4 = dash_table.DataTable(
    id='database-export-table-analytics',
    columns=[
        {'id': i, 'name': i, 'presentation': 'dropdown'}
        for i in export_table_data.columns
    ],
    data=export_table_data.to_dict('records'),
    page_current=0,  # page number that user is on
    page_size=10,
    export_format="csv")
    



layout = html.Div([
    dbc.Row( html.H1("ANALYTICS", style={'fontSize': 40, 'textAlign': 'center'})),
    html.Hr(),
    
    dbc.Row([
    dbc.Col(width = 2),
    dbc.Col(date_range_analytics1,width=2)
    ]),
    
    dbc.Row([
        dbc.Col(width = 2),
        dbc.Col(table1,width=2),
        dbc.Col(width = 1),
        dbc.Col([dcc.Graph(id="bar-graph-date-range-analytics", style={'width': '40vw', 'height': '30vh'})], width=4)        
    ]),
    
    
    html.H4('2. Attendance of employees by business unit in Date range',style={'fontSize': 25, 'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(date_range_analytics2, width=4),
        
        dbc.Col(width=3),
        dbc.Col([row3_BU], width=3),]
    ),
    dbc.Row([
        dbc.Col(width=2),
        dbc.Col(table3,width=2),
        dbc.Col(width = 1),
        dbc.Col([dcc.Graph(id="bar-graph-date-range-two-analytics", style={'width': '40vw', 'height': '30vh'})], width=4)]
    ),
    
    html.Hr(),
    
     dbc.Row([
        dbc.Col(width =2),
        dbc.Col([export_dropdown],width=4)
    ]),
     
        dbc.Row([
        dbc.Col(width =2),
        dbc.Col([table4],width=4)
    ])
    
   
    
   
    
    
    
    
    
    
    
])