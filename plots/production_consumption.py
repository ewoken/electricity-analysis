import plotly.graph_objects as go
import plotly.express as px
import numpy as np

TITLES = {
    'oil_prod_MW': 'Oil',
    'hard_coal_prod_MW': 'Hard coal',
    'gas_prod_MW': 'Gas',
    'nuclear_prod_MW': 'Nuclear',
    'wind_prod_MW': 'Wind',
    'solar_prod_MW': 'Solar',
    'hydro_prod_MW': 'Hydro',
    'bio_prod_MW': 'Bioenergies',
    'imports': 'Imports',
}
DEFAULT_COLORS = {
    'load_MW': '#000000',
    'oil_prod_MW': '#8356a2',
    'hard_coal_prod_MW': '#ac8c35',
    'gas_prod_MW': '#f30a0a',
    'nuclear_prod_MW': '#f5b300',
    'wind_prod_MW': '#74cdb9',
    'solar_prod_MW': '#f27406',
    'hydro_prod_MW': '#2772b2',
    'bio_prod_MW': '#166a57',
    'imports': '#505050',
    'exports': '#969696',
    'hydro_pumped_storage_MW': '#114774'
}
DEFAULT_ORDER = [
    'bio_prod_MW', 'nuclear_prod_MW', 'hydro_prod_MW', 'gas_prod_MW',
    'hard_coal_prod_MW', 'oil_prod_MW', 'wind_prod_MW', 'solar_prod_MW',
    'imports'
]

def plot_prod_consumption(df,
    start,
    end,
    title="",
    order=DEFAULT_ORDER,
    colors=DEFAULT_COLORS
):
    df = df[(start <= df['date_time']) & (df['date_time'] <= end)]
    df = df.sort_index()
    df['imports'] = np.maximum(0, df['total_physical_exchange_MW'])
    df['exports'] = np.minimum(0, df['total_physical_exchange_MW'])
    fig = go.Figure()

    x = list(df['date_time'])
    for prod_type in order:
        fig.add_trace(go.Scatter(
            name=TITLES[prod_type],
            x=x,
            y=list(df[prod_type] * 10**6),
            fillcolor=colors[prod_type],
            mode='none', # no line,
            stackgroup='prod'
        ))

    fig.add_trace(go.Scatter(
        name='Hydro pumped storage',
        x=x,
        y=list(df['hydro_pumped_storage_MW'] * 10**6),
        fillcolor=colors['hydro_pumped_storage_MW'],
        mode='none', # no line,
        stackgroup='neg'
    ))
    fig.add_trace(go.Scatter(
        name='Exports',
        x=x,
        y=list(df['exports'] * 10**6),
        fillcolor=colors['exports'],
        mode='none', # no line,
        stackgroup='neg'
    ))
    fig.add_trace(go.Scatter(
        name='Consumption',
        x=x,
        y=list(df['load_MW'] * 10**6),
        line={ 'color': colors['load_MW'], 'width': 1 }
    ))
    fig.update_layout(
        title_text=title,
        width=800,
        height=600,
        hovermode='x',
        margin={'b': 20, 't': 80}
    )
    fig.update_yaxes(exponentformat='SI', ticksuffix='W')
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    fig.show()
