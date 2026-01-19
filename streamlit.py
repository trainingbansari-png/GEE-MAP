

import streamlit as st
import ee
import folium
from streamlit_folium import st_folium
from datetime import date

# ----------------------------------
# Earth Engine Initialization
# ----------------------------------
import streamlit as st
import ee
import json

# Load EE credentials from Streamlit secrets
# Convert the Secrets object to a real dict first
ee_secrets = dict(st.secrets["ee"])
key_dict = json.loads(json.dumps(ee_secrets))

#credentials = ee.ServiceAccountCredentials(
#    key_dict["my-project@tactical-unison-484708-p7.iam.gserviceaccount.com"],
#    key_dict
#)
ee_creds = dict(st.secrets["ee"])
ee_creds["my-project@tactical-unison-484708-p7.iam.gserviceaccount.com"], 
    key_data=ee_creds["private_key"]
ee.Initialize(credentials)

st.success("Earth Engine initialized successfully")


# ----------------------------------
# Streamlit Configuration
# ----------------------------------
st.set_page_config(layout="wide")
st.title("🌍 Streamlit + Google Earth Engine")
st.success("Earth Engine initialized successfully!")

# ----------------------------------
# Sidebar Inputs
# ----------------------------------
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
# Search and Display Images
# ----------------------------------
if run:
    # ROI
    roi = ee.Geometry.Rectangle([lon_ul, lat_lr, lon_lr, lat_ul])

    # Satellite collections
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
        .sort("system:time_start")
    )

    count = collection.size().getInfo()
    st.write(f"🖼️ **Images Found:** {count}")

    if count == 0:
        st.warning("No images found for selected parameters.")
    else:
        # Use mosaic to visualize ALL images together
        selected_image = collection.mosaic()

        # -------------------------------
        # SAFE Image Date Handling
        # -------------------------------
        time_start = selected_image.get("system:time_start")

        image_date = ee.Algorithms.If(
            time_start,
            ee.Date(time_start).format("YYYY-MM-dd"),
            "Date not available (composite image)"
        )

        st.write(f"📅 **Image Date:** {ee.String(image_date).getInfo()}")

        # -------------------------------
        # Map Display
        # -------------------------------
        Map = geemap.Map(
            center=[(lat_ul + lat_lr) / 2, (lon_ul + lon_lr) / 2],
            zoom=8
        )

        Map.addLayer(roi, {}, "ROI")

        # Default visualization (no bands specified)
        Map.addLayer(
            selected_image,
            {},
            f"{satellite} Mosaic Image"
        )

        Map.to_streamlit(height=600)
