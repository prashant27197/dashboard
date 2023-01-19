# importing library
import dash
import dash_bootstrap_components as dbc
from dash import Input, State, Output, html, ctx
import sqlite3
from datetime import date
import pandas as pd
import calendar
from dash import dash_table
import base64
import datetime
import io
import plotly.express as px
import urllib



#defininig the app:
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server
print("=========================================================================================================================")
# connecting with the database
conn = sqlite3.connect('employees.db')
df = pd.read_sql_query(
    "SELECT m.employee_id,m.employee_name, m.business_unit, date,status FROM master as m INNER JOIN attendance UsING (employee_id)",
    conn)


#important functions:==============================================================================+
def calendar_date_to_string(date_value):
   date_value = date.fromisoformat(str(date_value)).strftime('%Y,%m,%d').split(',')
   date_value = datetime.date(int(date_value[0]), int(date_value[1]), int(date_value[2]))
   return date_value

def full_attendance_data():
    conn = sqlite3.connect('employees.db')
    df = pd.read_sql_query("SELECT * from attendance",conn)
    return df

def full_master_data():
    conn = sqlite3.connect('employees.db')
    df = pd.read_sql_query("SELECT * from master",conn)
    return df

def full_rto_data():
    conn = sqlite3.connect('employees.db')
    df = pd.read_sql_query("SELECT * from rto",conn)
    return df

def day_name_returner(date):
    dys = datetime.datetime.strptime(date, '%Y-%m-%d').weekday()
    dys =calendar.day_name[dys]
    return dys

    

#next daily record pusher
def next_day_record_pusher():
   df = full_attendance_data()
   try:
       if df['date'].max() < str(datetime.date.today()):
           conn = sqlite3.connect('employees.db')
           cur = conn.cursor()
           df = full_master_data()
           today = datetime.date.today()
           for ind in df.index:
               a = df['employee_id'][ind]
               query_insert = f"""INSERT OR IGNORE INTO attendance (employee_id,date,status)
                                                    VALUES({a},'{today}',0);"""
               cur.execute(query_insert)
               conn.commit()
               
           rto_df = full_rto_data()
           rto_max_date = rto_df['shift_date'].max()
           rto_df= rto_df[rto_df['shift_date']==str(rto_max_date)]

           for idx in rto_df.index:
                emp_id = rto_df['employee_id'][idx]
                today = datetime.date.today()
                last_sift_rec = rto_df['rto_days'][idx]
                query_insert = f"""REPLACE INTO rto (employee_id,shift_date,rto_days)
                                                    VALUES({emp_id},'{today}','{last_sift_rec}');"""
                cur.execute(query_insert)
                conn.commit()
   except Exception as e:
       print(e)


#sidebar of app:
sidebar = html.Div(
   [
       html.Div(
           [
               html.H2("ALCON", style={"color": "#288BA8"}),
           ],
           className="sidebar-header",
       ),
       html.Hr(),
       dbc.Nav(
           [
               dbc.NavLink(
                   [html.I(className="fas fa-home me-2"), html.Span("Dashboard")],
                   href="/",
                   active="exact",
               ),
               dbc.NavLink(
                   [
                       html.I(className="fas fa-calendar-alt me-2"),
                       html.Span("Analytics"),
                   ],
                   href="/analytics",
                   active="exact",
               ),
               dbc.NavLink(
                   [
                       html.I(className="fas fa-envelope-open-text me-2"),
                       html.Span("Uploads"),
                   ],
                   href="/master",
                   active="exact",
               ),
           ],
           vertical=True,
           pills=True,
       ),
   ],
   className="sidebar",
)

#layout of app:
app.layout = html.Div([
   dbc.Row([
       dbc.Col(sidebar, width=1),
       dbc.Col(dash.page_container, width=12)
   ]),
   next_day_record_pusher()

])


# 1.callbacks for dashboard:
#1.a Function 1: attandace updater
def attandace_updater(emp_id,date,status):
   if emp_id and date and status is None:
       raise dash.exceptions.PreventUpdate
   else:
       conn = sqlite3.connect('employees.db')
       cur = conn.cursor()
       query_insert = f""" REPLACE INTO attendance (employee_id,date,status)
                             VALUES('{emp_id}','{date}',{int(status)});"""
       cur.execute(query_insert)
       print('SUCESS')
       conn.commit()
       cur.close()
       return None
#1.b: Function 2: slicer by number of days:
def slicer(no_of_days):
    conn = sqlite3.connect('employees.db')
    cur = conn.cursor()    
    df = pd.read_sql_query(
    "SELECT m.employee_id,m.employee_name, m.business_unit, date,status FROM master as m INNER JOIN attendance UsING (employee_id)",
    conn)
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

#1.c:  Function:2 slicer for date range:
def range_slicer(start_date, end_date):
   conn = sqlite3.connect('employees.db')
   cur = conn.cursor()
   df = pd.read_sql_query(
    "SELECT m.employee_id,m.employee_name, m.business_unit, date,status FROM master as m INNER JOIN attendance UsING (employee_id)",
    conn)
   from_date = calendar_date_to_string(start_date)
   to_date = calendar_date_to_string(end_date)
   sliced_df = df[(df['date'] >= str(from_date)) &
                  (df['date'] <= str(to_date))]

   new_col = sliced_df['date'].unique()
   new_col.sort()
   sliced_df = sliced_df.pivot_table(index=['employee_id', "employee_name", 'business_unit'], columns=["date"],
                                     values='status')
   sliced_df = sliced_df.reset_index().rename_axis(None, axis=1)
   for i in new_col:
       dys = datetime.datetime.strptime(i, '%Y-%m-%d').weekday()
       sliced_df.rename(columns={i: i+"_"+calendar.day_name[dys]}, inplace=True)
   data = sliced_df.to_dict("records")
   cur.close()
   return data



#1.d. callback_dashboard
@app.callback(
   Output('datatable-interactivity-container', "children"),
   Input("datatable-interactivity-dashboard", "data"),
   State("datatable-interactivity-dashboard", "data_previous"),
   prevent_initial_call=True
)
def update(data_new,data):
    if data_new is None:
        data_new = data          
    try:  
        for row_index in range(len(data_new)):
            for column_name in data_new[row_index]:
                if data_new[row_index][column_name] != data[row_index][column_name]:
                    print(column_name,row_index)
                    status = data_new[row_index][column_name]
                    emp_id = data_new[row_index]['employee_id']
                    edit_date =column_name.split("_")[0]
                    print(emp_id)
                    print(status)
                    print(edit_date)
                    attandace_updater(emp_id,edit_date,status)
                    
    except Exception as e:
        print(e)


    
#1.e: Callback for business unit and date range:
@app.callback(
   Output('datatable-interactivity-dashboard', 'data'),
   Input("business-unit-dropdown-dashboard", "value"),
   Input('my-date-picker-range-dashboard', 'start_date'),
   Input('my-date-picker-range-dashboard', 'end_date'),
   Input("attandance-submit-btn", "n_clicks"),
   prevent_initial_call=True)
def update(value,start_date, end_date,n_click):
   triggered_id = ctx.triggered_id
   if triggered_id == 'business-unit-dropdown-dashboard':
       return update_accor_dropdown_table(value)
   elif triggered_id == 'my-date-picker-range-dashboard' and start_date is not None:
       return date_range_update(start_date, end_date)
   elif  triggered_id == 'attandance-submit-btn':
        return refresher(n_click)
     
def update_accor_dropdown_table(dropdown_value):
   data = slicer(6)
   df = pd.DataFrame(data)
   if dropdown_value is not None:
       filtered_df = df[df['business_unit'] == dropdown_value]
       data = filtered_df.to_dict("records")
       return data
   return data.to_dict("records")

def date_range_update(start_d, end_d):
   data = range_slicer(start_d, end_d)
   return data

def refresher(n_click):
    if n_click is None:
        raise dash.exceptions.PreventUpdate
    else:
        data= slicer(6)
        return data.to_dict('records')
    
    
    
    
    
#2. Callbacks for master upload
def parse_contents(contents, filename, date):
   content_type, content_string = contents.split(',')

   decoded = base64.b64decode(content_string)
   try:
       if 'csv' in filename:
           # Assume that the user uploaded a CSV file
           df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
           days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
           df['shift_days'] = df[days_of_week].apply(lambda row: ','.join([day for day, worked in zip(days_of_week, row) if worked == 1]), axis=1)

           # inserting the values:
           conn = sqlite3.connect('employees.db')
           cur = conn.cursor()
           for ind in df.index:
               a = df['Employee_id'][ind]
               b = df['Employee_Name'][ind]
               c = df['Business_Units'][ind]
               try:
                   cur = conn.cursor()
                   query_insert1 = f"""INSERT or REPLACE INTO master (employee_id,employee_name,business_unit)
                            VALUES({a},'{b}','{c}');"""
                   cur.execute(query_insert1)
                   conn.commit()
                   today = datetime.date.today()
                   query_insert2 = f"""INSERT or REPLACE INTO attendance (employee_id,date,status)
                                                VALUES({a},'{today}',0);"""
                   cur.execute(query_insert2)
                   conn.commit()
                     


                   shift_days = str(df['shift_days'][ind])
                   query_insert2 = f"""INSERT or REPLACE INTO rto (employee_id,shift_date,rto_days)
                                                VALUES({a},'{today}','{shift_days}');"""
                   
                   print('sucsess')
               except Exception as e:
                   print(e)
           cur.close()

       elif 'xlsx'  in filename:
           with open(f'{filename}', 'rb') as f:
                data = f.read()
           file_like = io.BytesIO(data)
           df = pd.read_excel(file_like)    
           days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
           df['shift_days'] = df[days_of_week].apply(lambda row: ','.join([day for day, worked in zip(days_of_week, row) if worked == 1]), axis=1)

           # inserting the values:
           conn = sqlite3.connect('employees.db')
           cur = conn.cursor()
           for ind in df.index:
               a = df['Employee_id'][ind]
               b = df['Employee_Name'][ind]
               c = df['Business_Units'][ind]
               try:
                   cur = conn.cursor()
                   query_insert1 = f"""INSERT or REPLACE INTO master (employee_id,employee_name,business_unit)
                            VALUES({a},'{b}','{c}');"""
                   cur.execute(query_insert1)
                   conn.commit()
                   today = datetime.date.today()
                   query_insert2 = f"""INSERT or REPLACE INTO attendance (employee_id,date,status)
                                                VALUES({a},'{today}',0);"""
                   cur.execute(query_insert2)
                   conn.commit()
                     


                   shift_days = str(df['shift_days'][ind])
                   query_insert2 = f"""INSERT OR REPLACE INTO rto (employee_id,shift_date,rto_days)
                                                VALUES({a},'{today}','{shift_days}');"""
                   cur.execute(query_insert2)
                   conn.commit()
                   
                   print('sucsessfully updated the shift')
               except Exception as e:
                   print(e)
           cur.close()
           
   except Exception as e:
       return html.Div([
           'There was an error processing this file.'
       ])

   return html.Div([
       html.H5(filename),
       html.H6(datetime.datetime.fromtimestamp(date)),

       dash_table.DataTable(
           df.to_dict('records'),
           [{'name': i, 'id': i} for i in df.columns]
       ),

       html.Hr(),  # horizontal line

       # For debugging, display the raw contents provided by the web browser
       html.Div('Raw Content'),
       html.Pre(contents[0:200] + '...', style={
           'whiteSpace': 'pre-wrap',
           'wordBreak': 'break-all'
       })
   ])

@app.callback(Output('output-data-upload', 'children'),
             Input('upload-data', 'contents'),
             State('upload-data', 'filename'),
             State('upload-data', 'last_modified'),
             prevent_initial_call=True)
def update_output(list_of_contents, list_of_names, list_of_dates):
   if list_of_contents is not None:
       children = [
           parse_contents(c, n, d) for c, n, d in
           zip(list_of_contents, list_of_names, list_of_dates)]
       return children

             
         

# 3. Callbacks for analytics:
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
@app.callback(Output('datatable-daterange-rto-interactivity-analytics', 'data'),
   Input('my-date-picker-range-analytics', 'start_date'),
   Input('my-date-picker-range-analytics', 'end_date'),
   prevent_initial_call=True)
def analytics_data_table(start_date,end_date):
   start_date = calendar_date_to_string(str(start_date))
   end_date = calendar_date_to_string(str(end_date))
   result = rto_status_finder(start_date,end_date)
   data = result.to_dict("records")
   return data
    
                
                
                
 # 3.b Bar Graph for rto table:
 
@app.callback(
   Output('bar-graph-date-range-analytics', 'figure'),
   Input('my-date-picker-range-analytics', 'start_date'),
   Input('my-date-picker-range-analytics', 'end_date'))
def update_output(start_date,end_date):
   
   df = rto_status_finder(start_date,end_date)
   
   piechart1 = px.pie(
       values=[df['RTO Attendance'].sum(),df['Total Attendance'].sum() -df['RTO Attendance'].sum()],
       names=['Present', 'Absent'],
       color=['Present', 'Absent'],
       #title=f"Organisation's attendace % on {date}" ,
       color_discrete_map={'Present': '#BDE17B',
                           'Absent': '#FF6347'},
       hole=.4)
   fig = px.bar(df, x="business_unit", y=["RTO Attendance","Total Attendance"], barmode='group', title="Bar Graph for RTO attendance")

   return fig





# 3c Date range and Bunits employee name wise analytics
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



@app.callback(Output('datatable-daterange-bunits-rto-interactivity-analytics', 'data'),
   Input('my-date-picker-range-two-analytics', 'start_date'),
   Input('my-date-picker-range-two-analytics', 'end_date'),
   Input('business-unit-dropdown-two-analytics','value'),
   prevent_initial_call=True)
def analytics_data_table1(start_date,end_date,business_unit):
   start_date = calendar_date_to_string(str(start_date))
   end_date = calendar_date_to_string(str(end_date))
   business_unit1 = str(business_unit)
   result = rto_status_bunits_finder(start_date,end_date,business_unit1)
   data = result.to_dict("records")
   return data



# 3 d Barchart for business unit specific employees rto attendance:

@app.callback(
   Output('bar-graph-date-range-two-analytics', 'figure'),
   Input('my-date-picker-range-two-analytics', 'start_date'),
   Input('my-date-picker-range-two-analytics', 'end_date'),
   Input('business-unit-dropdown-two-analytics','value'))
def update_output2(start_date,end_date,business_unit):
   
   df = rto_status_bunits_finder(start_date,end_date,business_unit)
   fig = px.bar(df, x="employee_name", y=["RTO Attendance","Total Attendance"], barmode='group', title="Bar Graph for Employee RTO attendance")

   return fig

#3.e callback for exporting the data:
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
@app.callback(
    Output('database-export-table-analytics', 'data'),
   Input('exportd-data-dropdown-analytics','value'),
   prevent_initial_call=True)

def export_data_by_dropdown(value):
    df = data_filter_for_export(value)
    return df.to_dict('records')
    
    



if __name__ == "__main__":
   app.run_server(port=8800, debug=True)