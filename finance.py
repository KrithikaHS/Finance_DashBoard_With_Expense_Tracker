import sqlite3
from flask import Flask, g
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import re
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css']
colors={
'background':'rgb(0,0,40)',
'color':'white'
}
font_family = 'sans-serif,Cursive, Arial'
# Database
DATABASE = "expenses.db"

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, check_same_thread=False)
    return db

def close_db(e=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# Flask initialization
server = Flask(__name__)
server.config.from_mapping(
    DATABASE=DATABASE,
)

server.teardown_appcontext(close_db)

# Dash app initialization
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.title = 'Expense Tracker and Financial Dashboard'

# Layout
app.layout = html.Div(children=[
    html.Div(id='alert-box'),
    html.H1("Personal Finance Dashboard With Expense Tracker"),

    dcc.Tabs(className="dash-tabs", children=[
        dcc.Tab(label='New Expense', id="Newview", className="dash-tab", children=[
            html.Div(className='tab-content', children=[
                html.Label('Date of the Expense (yyyy-mm-dd):'),
                dcc.Input(id='Date', type='text', placeholder="0000-00-00"),

                html.Label('Description of the Expense:'),
                dcc.Input(id='description', type='text', placeholder="What did you buy?"),

                html.Label('Category:'),
                dcc.Input(id='CATEGORY', type='text', placeholder='Category please!'),

                html.Label('Price of the Expense:'),
                dcc.Input(id='price', type="number", placeholder="0.00"),

                html.Button('Track', id='submit-button', n_clicks=0),
            ])
        ]),

        dcc.Tab(label='View Expenses', id="viewview", className="dash-tab", children=[
            html.Div(className='tab-content', children=[
                dcc.RadioItems(
                    id='view-selector',
                    className='radio-items',
                    options=[
                        {'label': 'View all expenses', 'value': 'all'},
                        {'label': 'View monthly expenses by category', 'value': 'monthly'},
                    ],
                    value='all'
                ),

                html.Div(id='expense-table', className='table-container'),
                html.Div(id='some-output-element'),
            ])
        ]),

        dcc.Tab(label='Yearly Transactions', id="yearview", className="dash-tab", children=[
            html.Div(className='tab-content', children=[
                html.H1("Yearly Dashboard"),
                dcc.Graph(id='graph_by_year', className='dash-graph', figure={'data': [], 'layout': {}})
            ])
        ]),

        dcc.Tab(label='Price based Line Chart', id="view-line", className="dash-tab", children=[
            html.Div(className='tab-content', children=[
                html.H1("Price Based Dashboard"),
                dcc.Graph(id='graph_by_price', className='dash-graph', figure={'data': [], 'layout': {}})
            ])
        ]),

        dcc.Tab(label='Category Based Pie Chart', id="catview", className="dash-tab", children=[
            html.Div(className='pie-chart-container', children=[
                dcc.Graph(id='pie_chart_category')
            ])
        ]),
    ])
])



@app.callback(
    Output('pie_chart_category', 'figure'),
    [Input('view-selector', 'value')]
)
def update_pie_chart_category(view_selector):
    conn = get_db()
    cur = conn.cursor()

    if view_selector == 'all':
        cur.execute("""SELECT Category, COUNT(*) AS Transactions
                       FROM expenses
                       GROUP BY Category""")
        category_data = cur.fetchall()
    else:
        cur.execute("""SELECT Category, COUNT(*) AS Transactions
                       FROM expenses
                       GROUP BY Category""")
        category_data = cur.fetchall()

    labels = [category[0] for category in category_data]
    values = [category[1] for category in category_data]

   
    custom_colors = [
    (255, 255, 255),  
    (255, 192, 203),  
    (245, 245, 220),  
    (144, 238, 144), 
    (173, 216, 230),  
    (255, 255, 153),  
    (230, 230, 250)   
]

    return {
        'data': [
            {
                'labels': labels,
                'values': values,
                'type': 'pie',
                'hoverinfo': 'label+percent',
                'textinfo': 'value+percent',
                'marker': {
                    'colors': custom_colors
                }
            },
        ],
        'layout': {
            'title': 'Transactions by Category (Pie Chart)',
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['color']
            }
        }
    }


@app.callback(
    Output('graph_by_year', 'figure'),
    [Input('view-selector', 'value')]
)
def update_graph_by_year(view_selector):
    conn = get_db()
    cur = conn.cursor()

    if view_selector == 'all':
        cur.execute("""SELECT strftime('%Y', Date) AS Year, COUNT(*) AS Transactions
                       FROM expenses
                       GROUP BY Year""")
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['Year', 'Transactions'])

        return {
            'data': [{'x': df['Year'], 'y': df['Transactions'], 'type': 'bar', 'name': 'Transactions by Year','margin-bottom':'400px', 'marker' : { "color" : "rgb(135, 206, 235)"}}],
            'layout': {
                'title': 'Number of transactions by year',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Number of transactions'},
                 'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'height':'400px',
                'font': {
                    'color': colors['color']
                }
            }
        }
    else:
        cur.execute("""SELECT strftime('%Y', Date) AS Year, COUNT(*) AS Transactions
                       FROM expenses
                       GROUP BY Year""")
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['Year', 'Transactions'])

        return {
            'data': [{'x': df['Year'], 'y': df['Transactions'], 'type': 'bar', 'name': 'Transactions by Year','margin-bottom':'400px', 'marker' : { "color" : "rgb(135, 206, 235)"}}],
            'layout': {
                'title': 'Number of transactions by year',
                'xaxis': {'title': 'Year'},
                'yaxis': {'title': 'Number of transactions'},
                 'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'height':'400px',
                'font': {
                    'color': colors['color']
                }
            }
        }

@app.callback(
    Output('graph_by_price', 'figure'),
    [Input('view-selector', 'value')]
)
def update_graph_by_price(view_selector):
    conn = get_db()
    cur = conn.cursor()

    if view_selector == 'all':
        cur.execute("""SELECT strftime('%Y-%m', Date) AS Month, AVG(Price) AS AveragePrice
                       FROM expenses
                       GROUP BY Month""")
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['Month', 'AveragePrice'])

        return {
            'data': [{'x': df['Month'], 'y': df['AveragePrice'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Average Price','marker' : { "color" : "crimson"}}],
            'layout': {
                'title': 'Average Price of transactions by month',
                'xaxis': {'title': 'Year(hover over line for month)'},
                'yaxis': {'title': 'Average Price'},
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['color']
                }
            }
        }
    else:
        cur.execute("""SELECT strftime('%Y-%m', Date) AS Month, AVG(Price) AS AveragePrice
                       FROM expenses
                       GROUP BY Month""")
        data = cur.fetchall()
        df = pd.DataFrame(data, columns=['Month', 'AveragePrice'])

        return {
            'data': [{'x': df['Month'], 'y': df['AveragePrice'], 'type': 'scatter', 'mode': 'lines+markers', 'name': 'Average Price','marker' : { "color" : "crimson"}}],
            'layout': {
                'title': 'Average Price of transactions by month',
                'xaxis': {'title': 'Year(hover over line for month)'},
                'yaxis': {'title': 'Average Price'},
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['color']
                }
            }
        }


@app.callback(
    Output('expense-table', 'children'),
    [Input('view-selector', 'value'),
     
    ]
)
def update_expense_table(view_selector):
    conn = get_db()
    cur = conn.cursor()

    if view_selector == 'all':
        cur.execute("SELECT * FROM expenses ORDER BY Date DESC")
        expenses = cur.fetchall()
        df = pd.DataFrame(expenses, columns=['ID', 'Date', 'Description', 'Category', 'Price'])


        if df.empty:
            return html.Div("No expenses recorded yet.", style={"color": "gray"})

        table = html.Table([
            html.Tr([html.Th(col) for col in df.columns])
        ] + [
            html.Tr([html.Td(row[col]) for col in df.columns]) for _, row in df.iterrows()
        ])

        return table

    elif view_selector == 'monthly':
        cur.execute("""SELECT strftime('%m', Date) AS Month, Category, SUM(Price) AS Total
                       FROM expenses
                       GROUP BY Month, Category""")
        monthly_expenses = cur.fetchall()
        monthly_df = pd.DataFrame(monthly_expenses, columns=['Month', 'Category', 'Total'])
        if monthly_df.empty:
            return 'No monthly expenses to display.'
        table = html.Table(
            [html.Tr([html.Th(column) for column in monthly_df.columns])] +
            [html.Tr([html.Td(expense[column]) for column in monthly_df.columns]) for _, expense in monthly_df.iterrows()]
        )
        return table

    return 'Invalid view type.'

@app.callback(
    [Output('some-output-element', 'children'),
     Output('Date', 'value'),
     Output('description', 'value'),
     Output('CATEGORY', 'value'),
     Output('price', 'value'),
     Output('alert-box', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('Date', 'value'),
     State('description', 'value'),
     State('CATEGORY', 'value'),
     State('price', 'value')]
)
def handle_form_submission(n_clicks, date, description, category, price):
    if n_clicks == 0:
        raise PreventUpdate

    # Basic validation
    if not description or not category or price is None:
        return ("", date, description, category, price, dbc.Alert("All fields are required.", color="warning"))

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (Date, description, CATEGORY, price) VALUES (?, ?, ?, ?)",
                    (date, description, category, price))
        conn.commit()
    except Exception as e:
        return ("", date, description, category, price, dbc.Alert(f"Error: {str(e)}", color="danger"))

    formatted_message = (
        f"Recent Expense:<br>"
        f"Date: {date}<br>"
        f"Description: {description}<br>"
        f"Category: {category}<br>"
        f"Price: {price}"
    )
    return (dcc.Markdown(formatted_message, dangerously_allow_html=True), '', '', '', 0,
            dbc.Alert("Expense added successfully!", color="success", dismissable=True))






if __name__ == '__main__':
    app.run(debug=True)
