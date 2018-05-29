# -*- coding: utf-8 -*-
"""
Created on Sat May 26 16:10:40 2018

@author: Amjee
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Event, Input
import plotly.graph_objs as go
import plotly
import pandas as pd 
import sqlite3

#os.system(r'C:\Users\Amjee\Anaconda3\myworks\tweetyment.py')
#tweet_db = pd.read_csv('C:\\Users\\Amjee\\Anaconda3\\myworks\\tweetytext.csv',names=['datetime','sentiment','tweets'])

app = dash.Dash()

my_css_url = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
app.css.append_css({
    "external_url": my_css_url
})

app.layout = html.Div(children=[
    html.H3(children='Real-time Twitter sentiment analysis',style={
            'textAlign': 'center',
            'color' : '#9400D3',
            }),

html.Div(children='''
        Type your hastag below.
    ''',),
   
    dcc.Input(placeholder='Search...',type='text',value='a',id='searchstring'),
    html.Div(id='output-graph'),     
    dcc.Graph(id='example-graph',animate=False),
    dcc.Interval( id='graph-update',interval=1*1000),   
        ])

@app.callback(Output('example-graph', 'figure'),
                  [Input(component_id='searchstring', component_property='value')],
                  events=[Event('graph-update', 'interval')]
                  )


def update_graph(searchstring):
  try:  
        conn = sqlite3.connect('tweeter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY datetime DESC LIMIT 1000", conn ,params=('%' + searchstring + '%',))
        df.sort_values('datetime', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)
    
        X = df.datetime.values[-100:]
        Y = df.sentiment_smoothed.values[-100:]
    
        data = plotly.graph_objs.Scatter(
                    x=X,
                    y=Y,
                    name='Scatter',
                    mode= 'lines+markers'
                    )
    
        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                        yaxis=dict(range=[min(Y),max(Y)]),)}
  except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

    


if __name__ == '__main__':
    app.run_server(debug=True)