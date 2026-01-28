import streamlit as st
import ee
import geemap
import folium
#import geemap.foliumap as gmf # Ensure geemap is imported
from datetime import date
import json

# 1. MUST BE FIRST
st.set_page_config(layout="wide")

# 2. Earth Engine Initialization
if "ee" in st.secrets:
    try:
        ee_creds = dict(st.secrets["ee"])
        # The replace ensures the RSA key is formatted correctly
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

# ----------------------------------
# Streamlit UI
# ----------------------------------
st.title("🌍 Streamlit + Google Earth Engine")

with st.sidebar:
    st.header("🔍 Search Parameters")
    lat_ul = st.number_input("Upper-Left Latitude", value=22.5)
    lon_ul = st.number_input("Upper-Left Longitude", value=68.0)
    lat_lr = st.number_input("Lower-Right Latitude", value=21.5)
    lon_lr = st.number_input("Lower-Right Longitude", value=69.0)

    satellite = st.selectbox(
        "Satellite",
        ["Sentinel-2", "Landsat-8", "Landsat-9", "MODIS"]
    )
    start_date = st.date_input("Start Date", date(2024, 1, 1))
    end_date = st.date_input("End Date", date(2024, 12, 31))
    run = st.button("🚀 Search Images")

# ----------------------------------
# Processing
# ----------------------------------
if run:
    roi = ee.Geometry.Rectangle([lon_ul, lat_lr, lon_lr, lat_ul])

    collection_ids = {
        "Sentinel-2": "COPERNICUS/S2_SR_HARMONIZED",
        "Landsat-8": "LANDSAT/LC08/C02/T1_L2",
        "Landsat-9": "LANDSAT/LC09/C02/T1_L2",
        "MODIS": "MODIS/006/MOD09GA"
    }

    collection = (
        ee.ImageCollection(collection_ids[satellite])
        .filterBounds(roi)
        .filterDate(str(start_date), str(end_date))
    )

    count = collection.size().getInfo()
    st.write(f"🖼️ **Images Found:** {count}")

    if count > 0:
        selected_image = collection.median().clip(roi) # Use median for a cleaner mosaic
        
        # Setup Map
        Map = geemap.Map(center=[(lat_ul + lat_lr) / 2, (lon_ul + lon_lr) / 2], zoom=8)
        
        # Visualization parameters (Sentinel-2 True Color example)
        vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.4} if satellite == "Sentinel-2" else {}
        
        Map.addLayer(selected_image, vis_params, f"{satellite} True Color")
        geojson = folium.GeoJson(roi.getInfo(), name="ROI")
        geojson.add_to(Map)
        # Display map
        Map.to_streamlit(height=600)
