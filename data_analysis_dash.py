# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv('spacex_launch_dash.csv')

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 30}),
    html.Div([
        html.Label("Select a launch site"),
        dcc.Dropdown(id='site-dropdown',
                     options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                         {'label': site, 'value': site}
                         for site in spacex_df['Launch Site'].unique()
                     ], placeholder='Select a Launch Site here',
                     value='ALL',
                     searchable=True
                    )
    ]),
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.Div([
        html.Label("Select payload range (kg)"),
        dcc.RangeSlider(id='payload-slider',
                        min=0,
                        max=10000,
                        step=1000,
                        value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]
                       )
    ]),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])


@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_rate = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_rate, values='class', names='Launch Site', title='Total Success Launches By Site')
        return fig
    else:
        spacex_df_filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_rate = spacex_df_filtered.groupby('class')['class'].count()
        fig = px.pie(success_rate, values='class', names=success_rate.index, title=f'Total Success Launches for site {entered_site}')
        return fig


@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_mass):
    if entered_site == 'ALL':
        spacex_df_filtered = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_mass[0]) & (spacex_df['Payload Mass (kg)'] <= payload_mass[1])]
        fig = px.scatter(spacex_df_filtered, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        spacex_df_filtered = spacex_df[(spacex_df['Launch Site'] == entered_site) & (spacex_df['Payload Mass (kg)'] >= payload_mass[0]) & (spacex_df['Payload Mass (kg)'] <= payload_mass[1])]
        fig = px.scatter(spacex_df_filtered, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=f'Correlation between Payload and Success for {entered_site}')
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)