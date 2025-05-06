import pandas as pd
import plotly.express as px
import yaml

municipalities_per_state = {}
file_path = '2024_Gaz_place_national.txt'
with open(file_path, 'r') as file:
    keys = file.readline().strip().split('\t')
    keys = ['state' if key == 'USPS' else key for key in keys]

    data = []
    for line in file:
        values = []
        value = line.strip().split('\t')
        values.append(value)  
        data.append(dict(zip(keys, value)))

census_df = pd.DataFrame(data)
municipalities_per_state = census_df.groupby('state').size().reset_index(name='municipalities_count')

open_states_municipalities_df = pd.DataFrame()

states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia',
          'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj',
          'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt',
          'va', 'wa', 'wv', 'wi', 'wy']

for s in states:
    file_path = f'data/{s}/municipalities.yml'
    with open(file_path, 'r') as file:
        yaml_data = yaml.safe_load(file)
        if not yaml_data:
            print(f"No data found in {file_path}")
            continue
        df = pd.DataFrame(yaml_data)
        df.insert(0, 'state', s.upper())
        open_states_municipalities_df = pd.concat([open_states_municipalities_df, df], ignore_index=True)

existing_municipalities_per_state = open_states_municipalities_df.groupby('state').size().reset_index(name='existing_count')
merged_df = pd.merge(municipalities_per_state, existing_municipalities_per_state)
merged_df['percentage_complete'] = (merged_df['existing_count'] / merged_df['municipalities_count'])*100

fig = px.choropleth(
    merged_df,
    locations='state',
    locationmode='USA-states',
    color='percentage_complete',
    color_continuous_scale='Viridis',
    scope='usa',
    labels={'percentage_complete': 'Percentage of Municipalities with Data'},
    title='How many municipalities currently have data available in OpenStates?',
    hover_name='state',
    hover_data=['existing_count', 'municipalities_count'],
)

fig.show()