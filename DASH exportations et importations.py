import dash
from dash import  dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {
 'background': '#3c4249',
 'text': '#8eb4bd'
}

df = pd.read_csv(r"C:\Users\dell\Downloads\ExportData.csv",sep=";",decimal=',',low_memory=False)
df_expo=df[df['Libellé du flux']=='Exportations FAB']
df_impo=df[df['Libellé du flux']=='Importations CAF']


def fct_data(année, flux):
    df_impo_ex = df[df['Libellé du flux'] == flux]
    data = df_impo_ex.loc[:, df_impo_ex.columns.str.startswith('Valeur') & df_impo_ex.columns.str.endswith(année)]
    dataa = df_impo_ex.loc[:, ['Libellé du pays', 'Continent', 'Code du pays']]
    datayear = pd.concat([data, dataa], axis=1)
    s = datayear.groupby(['Libellé du pays', 'Code du pays', 'Continent']).sum().sum(axis=1)
    s = s.reset_index()
    s = s.rename(columns={0: 'valeur_DH'})
    s['année'] = int(année)
    s['flux'] = flux
    return s


def fct_flux(flux):
    return pd.concat([fct_data('2017', flux), fct_data('2018', flux), fct_data('2019', flux), fct_data('2020', flux)])


result = pd.concat([fct_flux('Exportations FAB'), fct_flux('Importations CAF')])

evolution = result.groupby(['flux', 'année']).sum().reset_index()

fig_2 = px.line(evolution, x="année", y="valeur_DH", color='flux',template="plotly_dark",color_discrete_sequence=['indianred','lightsalmon'])
fig_2.update_layout(
    xaxis_title="année",
    yaxis_title="valeur en Millions de DH"
)
fig_2.update_traces(mode='lines+markers')
fig_2.update_xaxes(type='category')

# graphe scatter

scatt1=fct_flux('Importations CAF').rename(columns={"valeur_DH":"importationDH"})

scatterdata=pd.merge(scatt1.drop('flux',axis=1),fct_flux('Exportations FAB').rename(columns={"valeur_DH":"exportationDH"}).drop('flux',axis=1),how='outer',on=['Libellé du pays','année','Continent','Code du pays'])
m=scatterdata.dropna()
fig_3 = px.scatter(m, x="importationDH", y="exportationDH",animation_frame="année", color="Continent",hover_name="Libellé du pays",template="plotly_dark")



# evolution_ mois
def evolution_mois(année,flux):
  data =df_impo
  if flux=='Exportations FAB':
    data=df_expo
  data2=data.loc[:,data.columns.str.startswith('Valeur')]
  mois_evolution= pd.DataFrame({"Date":pd.date_range(start='2017-01-01',
                                          periods=48,freq='M'
                                  ),"valeur totale en DHS":data2.iloc[:,0].sum()})
  for i in range(len(mois_evolution)):
      mois_evolution.loc[:, "valeur totale en DHS"][i] = data2.iloc[:, i].sum()
  j = 0
  if année == 2017: j = 0
  if année == 2018: j = 12
  if année == 2019: j = 24
  if année == 2020: j = 36
  mois_evolution = mois_evolution.iloc[0 + j:11 + j]

  return mois_evolution
# world map
iso_alpha=pd.read_csv(r'C:\Users\dell\Downloads\sql-pays.csv')
iso_alpha=iso_alpha.iloc[:,3:5]
iso_alpha=iso_alpha.rename(columns={'AFG':'iso_alpha3','Afghanistan':'Libellé du pays'})
iso_alpha.iloc[0]=['AFG','Afghanistan']
dict = {'iso_alpha3': 'Vikram', 'Libellé du pays': 'YOUGOUSLAVIE	'}
iso_alpha = iso_alpha.append(dict, ignore_index = True)
iso_alpha['Libellé du pays'] = iso_alpha['Libellé du pays'].str.upper()
cols = iso_alpha.select_dtypes(include=[object]).columns
iso_alpha[cols] = iso_alpha[cols].apply(lambda x: x.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))




app.layout =html.Div(style={'backgroundColor': colors['background']},children=[
             html.H1(
             children='Dash: Commerce extérieur du MAROC',
             style={
             'textAlign': 'center',
             'color': colors['text']
             }
             ),

            html.Div([
                html.Div([
                    html.H5(children='valeur des importations et exportations par continent',
                            style={'textAlign': 'center', 'color': colors['text']}),
                    html.Br(),
                    html.Br(),

                    dcc.Graph(
                             id='graph3',
                             figure=fig_3
                         ),
                     ], className='five columns'),
                html.Div([
                    html.H5(children='carte mondiale des importations et exportations par pays ',
                            style={'textAlign': 'center', 'color': colors['text']}),
                    html.Label("flux:", style={'color': colors['text']}),
                    dcc.Dropdown(
                        id="flux",
                        value='Exportations FAB',
                        options=[{'value': x, 'label': x}
                                 for x in ['Exportations FAB', 'Importations CAF']],
                        clearable=False,
                        style={'width': "40%"}),
                    dcc.Graph(
                        id='graph6'),
                ], className='seven columns')],className='one row'),


        html.Div([

                html.Div([
                    html.Br(),

                    html.H5(children="commerce extérieur du Maroc",
                                style={'textAlign': 'center', 'color': colors['text']}),
                    html.Br(),
                    html.Br(),

                    dcc.Graph(
                         id='graph2',
                         figure=fig_2
                     ),


                ], className='five columns'),

                html.Div([
                html.Br(),

                html.H5(children='evolution des importations et exportations par année',style={'textAlign': 'center','color': colors['text']}),
                html.Label("année:", style={'color': colors['text']}),

                dcc.Dropdown(
                id="an",
                value=2017,
                options=[{'value': x, 'label': x}
                         for x in [2017,2018,2019,2020]],
                clearable=False,
                style = {'width': "40%"}),
                dcc.Graph(
                    id='graph5',
                )], className='seven columns')],className='one row'),


                html.Div([
                    html.Div([
                    html.Br(),

                    html.H5(children='distribtion des produits',
                    style={'textAlign': 'center', 'color': colors['text']}),
                    html.Label("flux:", style={'color': colors['text']}),
                    html.Div([
                            dcc.Dropdown(
                                id="type_de_flux",
                                value="Importations CAF",
                                options=[{'value': x, 'label': x}
                                         for x in ["Importations CAF","Exportations FAB"]],
                                clearable=False,
                                style = {'width': "40%"}),

                            dcc.Dropdown(
                            id="année",
                            value=2017,
                            options=[{'value': x, 'label': x}
                                     for x in [2017,2018,2019,2020]],
                            clearable=False,
                            style = {'width': "40%"})],className='one row'),
                    dcc.Graph(
                        id='pie-chart')], className='seven columns'),

                    html.Div([
                    html.Br(),

                    html.H5(children='valeur des importations et exportations par continent',style={'textAlign': 'center','color': colors['text']}),
                    html.Br(),
                    html.Br(),
                    html.Label("année:", style={'color': colors['text']}),
                    dcc.Dropdown(
                    id="year",
                    value=2017,
                    options=[{'value': x, 'label': x}
                             for x in [2017,2018,2019,2020]],
                    clearable=False,
                    style = {'width': "40%"}),
                    dcc.Graph(
                        id='graph4',
                )] ,className='five columns')],className='one row'),


])

@app.callback(
    Output("graph4", "figure"),
    [Input("year", "value")]
)
def generate_chart(year):
    bar_data=result[result['année']==year]
    fig_4 = px.bar(bar_data, x="Continent", y="valeur_DH",
                   color="flux", barmode='group', template='plotly_dark',color_discrete_sequence=['indianred','lightsalmon'])
    fig_4.update_traces(marker_line_width=0)

    return fig_4



@app.callback(
    Output("pie-chart", "figure"),
    [Input("année", "value"),Input("type_de_flux", "value")]
)
def generate_chart(année,type_de_flux):
 df_impo_ex = df[df['Libellé du flux'] == type_de_flux]
 test = df_impo_ex.groupby("Libellé du groupement d'utilisation").sum()
 df_impex_year = test.loc[:, test.columns.str.startswith('Valeur') & test.columns.str.endswith(str(année))]
 df_impex_year.sum(axis=1)
 fig = px.pie(values=df_impex_year.sum(axis=1), names=df_impex_year.sum(axis=1).index,template='plotly_dark',color_discrete_sequence=px.colors.sequential.Sunset)

 return fig

@app.callback(
    Output("graph5", "figure"),
    [Input("an", "value")]
)
def generate_chart(year):


    fig = go.Figure(data=[
        go.Bar(name='valeur des produits importés', x=evolution_mois(year, 'Importations CAF')["Date"],
               y=evolution_mois(year, 'Exportations CAF')["valeur totale en DHS"],marker={'color':'#e4a89f'}),
        go.Bar(name='valeur des produits exportés', x=evolution_mois(year, 'Exportations FAB')["Date"],
               y=evolution_mois(year, 'Exportations FAB')["valeur totale en DHS"],marker={'color':'#f3e79b'})
    ])
    fig.update_xaxes(color='white')
    fig.update_yaxes(color='white')
    fig.update_layout(template='plotly_dark')
    return fig

@app.callback(
    Output("graph6", "figure"),
    [Input("flux", "value")]
)
def generate_chart(flux):

    data_flux = fct_flux(flux)
    mapdata = pd.merge(data_flux, iso_alpha, how='outer', on='Libellé du pays')
    mapdata = mapdata.dropna()
    fig_6 = px.scatter_geo(mapdata, locations="iso_alpha3", color="Continent", opacity=.8,
                           hover_name="Libellé du pays", size='valeur_DH', hover_data=['valeur_DH', 'Libellé du pays'],
                           projection="natural earth", animation_frame='année',template='plotly_dark')
    return fig_6


if __name__ == '__main__':
 app.run_server(debug=True)