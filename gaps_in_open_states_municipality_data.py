import pandas as pd
import plotly.express as px
import os

# TODO: This may be replaced with data in the municipalities.yaml files from the OpenStates repo 
municipalities_per_state = {}
file_path = '2024_Gaz_place_national.txt'
with open(file_path, 'r') as file:
    keys = file.readline().strip().split('\t')
    keys = ['state' if key == 'USPS' else key for key in keys]

    data = []
    for line in file:
        value = line.strip().split('\t')
        data.append(dict(zip(keys, value)))

census_df = pd.DataFrame(data)
municipalities_per_state = census_df.groupby('state').size().reset_index(name='municipalities_count')
# End Census data analysis

# Begin OpenStates data analysis
open_states_municipalities_df = pd.DataFrame()

states = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia',
          'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj',
          'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt',
          'va', 'wa', 'wv', 'wi', 'wy']

existing_municipalities_per_state = pd.DataFrame(columns=['state', 'existing_count'])

for s in states:
    directory_path = f'data/{s}/municipalities/'
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist")
        continue
    try: 
        file_count = len([name for name in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, name))])
    except FileNotFoundError:
        print(f"Directory {directory_path} is empty")
        continue
    
    existing_municipalities_per_state = pd.concat(
        [existing_municipalities_per_state, pd.DataFrame({'state': [s.upper()], 'existing_count': [file_count]})],
        ignore_index=True
    )

merged_df = pd.merge(municipalities_per_state, existing_municipalities_per_state, on='state', how='outer')
merged_df['percentage_complete'] = (merged_df['existing_count'] / merged_df['municipalities_count'])*100
merged_df['existing_count'] = merged_df['existing_count'].fillna(0)  # Handle missing values
merged_df['municipalities_count'] = merged_df['municipalities_count'].fillna(0)
merged_df['percentage_complete'] = merged_df['percentage_complete'].fillna(0)

fig = px.choropleth(
    merged_df,
    locations='state',
    locationmode='USA-states',
    color='percentage_complete',
    color_continuous_scale='Viridis',
    scope='usa',
    labels={'percentage_complete': 'Percentage of Municipalities with Data'},
    title='How complete is the municipalities data in OpenStates?',
    hover_name='state',
    hover_data={'existing_count': True, 'municipalities_count': True, 'percentage_complete': True},
)

fig.show()