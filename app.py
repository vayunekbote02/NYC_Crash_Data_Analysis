import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import plotly.express as px


@st.cache(persist=True)
def load_data(nrows):
    df = pd.read_csv("VehicleCrashes.csv", nrows=nrows,
                     parse_dates=[["CRASH_DATE", "CRASH_TIME"]])
    df.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    def lowercase(x): return str(x).lower()
    df.rename(mapper=lowercase, axis=1, inplace=True)
    df.rename(columns={'crash_date_crash_time': 'date_time'}, inplace=True)
    return df


def load_css(filename):
    with open(filename) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


df = load_data(100_000)
df_end = df.copy()

# Main Website
st.write("# NYC Crash Analysis")
st.markdown("Data of vehicle crashes in NYC")
value = st.slider(
    "Choose the number of injured people in single accident", 0, 19, 10)
st.map(df.query(f"injured_persons >= {value}")[
       ["latitude", "longitude"]].dropna(how="any"))

st.header("Collisions acc to time of the day")
hour = st.slider("Select hour of the day", 0, 23)
df = df[df['date_time'].dt.hour == hour]

st.markdown(f"Collision density between {hour}:00 and {hour+1}:00.")

midpoint = (np.average(df["latitude"]), np.average(df["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=df[['date_time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True, pickable=True,
            elevation_scale=4, elevation_range=[0, 1000],
        ),
    ]
))

st.subheader(f"Collisions in every minute between {hour}:00 and {hour+1}:00.")
filtered_data = df[(df['date_time'].dt.hour >= hour) &
                   (df['date_time'].dt.hour < (hour+1))]
histogram = np.histogram(
    filtered_data['date_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minutes': range(60), 'crashes': histogram})
fig = px.bar(chart_data, x='minutes', y='crashes',
             hover_data=['minutes', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 street affected by type")
type = st.selectbox("Type of People", ["Pedestrians", "Cyclists", "Motorists"])
if type == "Pedestrians":
    ret = df_end.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(
        by="injured_pedestrians", ascending=False).dropna(how="any")[:5]
    st.write(ret)
elif type == "Cyclists":
    ret = df_end.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(
        by="injured_cyclists", ascending=False).dropna(how="any")[:5]
    st.write(ret)
else:
    ret = df_end.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(
        by="injured_motorists", ascending=False).dropna(how="any")[:5]
    st.write(ret)


load_css("index.css")
if st.checkbox("Show data table"):
    st.subheader("Raw Data")
    st.write(df)
