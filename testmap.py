import streamlit as st
import geemap

# Initialize the map (simple test without any layers)
st.set_page_config(layout="wide")
st.title("🌍 Streamlit + Geemap Test")

# Create a simple map to test
Map = geemap.Map(center=[22.5, 68.0], zoom=8)

# Display the map in Streamlit
try:
    Map.to_streamlit(height=600)
    st.write("Map displayed successfully.")
except Exception as e:
    st.error(f"Error displaying map: {e}")
