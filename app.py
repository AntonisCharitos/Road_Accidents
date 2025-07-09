
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(page_title="USA Car Accidents Dashboard", layout="wide")

st.title("🚗 USA Car Accidents (2016–2023) Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("US_Accidents_March23.csv", low_memory=False)

    # Convert Start_Time to datetime
    df['Start_Time'] = pd.to_datetime(df['Start_Time'], errors='coerce')

    # Drop rows with missing location data
    df = df.dropna(subset=['Start_Lat', 'Start_Lng'])

    # Sample the data (change n as needed)
    df = df.sample(n=2_000_000, random_state=42)  # Or use frac=0.1 for 10%

    # Feature engineering
    df['Hour'] = df['Start_Time'].dt.hour
    df['DayOfWeek'] = df['Start_Time'].dt.day_name()
    df['Date'] = df['Start_Time'].dt.date

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

state = {
    'OH': 'Ohio',
    'WV': 'West Virginia',
    'CA': 'California',
    'FL': 'Florida',
    'GA': 'Georgia',
    'SC': 'South Carolina',
    'NE': 'Nebraska',
    'IA': 'Iowa',
    'IL': 'Illinois',
    'MO': 'Missouri',
    'WI': 'Wisconsin',
    'IN': 'Indiana',
    'MI': 'Michigan',
    'NJ': 'New Jersey',
    'NY': 'New York',
    'CT': 'Connecticut',
    'MA': 'Massachusetts',
    'RI': 'Rhode Island',
    'NH': 'New Hampshire',
    'PA': 'Pennsylvania',
    'KY': 'Kentucky',
    'MD': 'Maryland',
    'VA': 'Virginia',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'TX': 'Texas',
    'WA': 'Washington',
    'OR': 'Oregon',
    'AL': 'Alabama',
    'NC': 'North Carolina',
    'AZ': 'Arizona',
    'TN': 'Tennessee',
    'LA': 'Louisiana',
    'MN': 'Minnesota',
    'CO': 'Colorado',
    'OK': 'Oklahoma',
    'NV': 'Nevada',
    'UT': 'Utah',
    'KS': 'Kansas',
    'NM': 'New Mexico',
    'AR': 'Arkansas',
    'MS': 'Mississippi',
    'ME': 'Maine',
    'VT': 'Vermont',
    'WY': 'Wyoming',
    'ID': 'Idaho',
    'ND': 'North Dakota',
    'MT': 'Montana',
    'SD': 'South Dakota'
}

df['State'] = df['State'].map(state)


states = df['State'].dropna().unique()
selected_state = st.sidebar.selectbox("Select State", ["All States"] + sorted(states))

weather_options = df['Weather_Condition'].dropna().unique()
selected_weather = st.sidebar.multiselect("Weather Conditions", sorted(weather_options))

days = df['DayOfWeek'].dropna().unique()
selected_days = st.sidebar.multiselect("Day of the Week", sorted(days))

hour_range = st.sidebar.slider("Hour of Day", 0, 23, (0, 23))

fatal_only = st.sidebar.checkbox("Show Only Fatal Accidents", value=False)

# Apply filters
if selected_state != "All States":
    filtered_df = df[df['State'] == selected_state]
else:
    filtered_df = df.copy()

if selected_weather:
    filtered_df = filtered_df[filtered_df['Weather_Condition'].isin(selected_weather)]

if selected_days:
    filtered_df = filtered_df[filtered_df['DayOfWeek'].isin(selected_days)]

filtered_df = filtered_df[(filtered_df['Hour'] >= hour_range[0]) & (filtered_df['Hour'] <= hour_range[1])]

if fatal_only:
    filtered_df = filtered_df[filtered_df['Severity'] == 4]

st.markdown(f"### Showing {len(filtered_df)} accidents in {selected_state}")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Accidents by Day of Week")
    day_counts = filtered_df['DayOfWeek'].value_counts().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    st.bar_chart(day_counts)

with col2:
    st.subheader("Accidents by Hour")
    st.bar_chart(filtered_df['Hour'].value_counts().sort_index())

st.subheader("Accidents by Weather Condition")
weather_counts = filtered_df['Weather_Condition'].value_counts().head(10)
st.bar_chart(weather_counts)

# Map
st.subheader("📍 Accident Locations Map")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=filtered_df['Start_Lat'].mean(),
        longitude=filtered_df['Start_Lng'].mean(),
        zoom=6,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered_df[['Start_Lat', 'Start_Lng']].dropna(),
            get_position='[Start_Lng, Start_Lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=100,
            pickable=True,
        ),
    ],
))