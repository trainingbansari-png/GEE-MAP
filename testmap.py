import streamlit as st
import geemap
import ee
from datetime import date

# Initialize the map (basic check)
st.set_page_config(layout="wide")
st.title("🌍 Streamlit + Google Earth Engine - Test Map")

# Earth Engine Initialization
if "ee" in st.secrets:
    try:
        ee_creds = dict(st.secrets["ee"])
        fixed_key = ee_creds["private_key"].replace("\\n", "\n")
        
        credentials = ee.ServiceAccountCredentials(
            ee_creds["client_email"], 
            key_data=fixed_key
        )
        ee.Initialize(credentials)
        st.sidebar.success("Earth Engine initialized!")
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        st.stop()
else:
    st.error("EE secrets not found.")
    st.stop()

# Test if geemap map is working without layers
Map = geemap.Map(center=[22.5, 68.0], zoom=10)

try:
    Map.to_streamlit(height=600)  # This should render the map in Streamlit
    st.write("Map displayed successfully")
except Exception as e:
    st.error(f"Error displaying map: {e}")
