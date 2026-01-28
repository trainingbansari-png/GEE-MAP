import streamlit as st
import ee
import geemap
from datetime import date
from google.oauth2 import service_account  # Correct import for credentials
from google.auth.transport.requests import Request  # Optional, used for token refresh

# 1. MUST BE FIRST
st.set_page_config(layout="wide")

# 2. Earth Engine Initialization
if "ee" in st.secrets:
    try:
        ee_creds = dict(st.secrets["ee"])
        # The replace ensures the RSA key is formatted correctly
        fixed_key = ee_creds["private_key"].replace("\\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCYnJx2zTFgfpdS\nTXL2leBz82J9b4PvDnaLWulengKjNVyrueqZgPR1QuKvGQCPp3Jt2TouuKVWemrz\nEQeNzsEo45zUocBVzqWIQsuMur3UDBpZVWilpv4xN9npm5aYoYgIm9KbwWQmHavO\nDIHODc2AgTsuGQKEO40ISPanwP5PxDuxUAPNbc1W6GdSj+swMtIu4ecApSGzWjGB\n1EFouLgCQI89L8F1lvzDWe9OCRJydpKoSV++Bf32lKY82mH0o5Oeu4NJSldakGnP\nYFVFPa9ljr8a/V6QBcNEz+pxbdeg1lNF6ljW/ABvFFrCKB/BzTHtmfyNbhVZqmx+\nXfspse4pAgMBAAECggEAD4eYUGqPBL+9DE3/TeJwhbwVoKgRZ+kz3PhyWQOBRzRt\n6revjNFXjvswcBr+OKAUf+MkDY8SnBs2+OcZuq94bn3C/sw680BlDdmmNvrlyEc3\nAzIyxPCaW03QqfoAOCXv3thkdR8X3t0UF5KkPuCesd30tLssy2H39wjduLJl7p3k\nLK5xMA8wgwsZFy6IWSwzOm4rRgsjsZAK3mPAFVSkIFgSEwq/dXa3yx8XXEnHoHTl\nDOFC033OmtdToZ0/O2+69aH2t5AK8KiL5Ymd6GmDfhuXWayrkSN11aSTprXp9XFG\nSuc/aI2VcRkF+wGPAduDA31PBXXOyDVqdIBaAKsJNQKBgQDJxcQSCGVDH9uRMxRk\nRYymEvv0vA927LRTreUMLaeChv0MKFFlQ7oZ3TgIZF5BD+OqHm2cgacaNJ4oEWwe\njgjrykeuyYfyi06vVi4MAp7RkGRT1UK0ePpJOuIp7P81WKdWarIg8C9O1/OJS2bu\nR5gMjoOPdpmUUz0stbZnWLX+6wKBgQDBoIQA3+2IP5ZBU28bmV0bdqD6IQXXvPI9\nPYMX3KWYBTesRBdEp9s5z/MNSOYg3+LPSe7QS/g9hNqk+xF9JXasE62Wo1pYzlrt\nVRflwtqZhOVruQqnGmv7SEqFZBbHnlBk6lyO+E3dXP46moKfZoikRwHBKiUlFrHv\nhUspXqEKOwKBgDNRFRjxAbAcvh8jup/2AFuMoIASBGzers5Jf+OlCOFtq5YX+vui\nSgah+MpJnJ83h1ORAZe4ceN8Vm0iYTk0Lpipjamqn+TUAWMeq/9p+zKZYqrfpmN4\nEU/mpfa7y/ypW4XjBQLTk3Sd/9Z/UuJvWwB2jodCRrUupnRkksueCEuZAoGAGggl\nlySD/9xkrBW2i2RcEzQowlgsO+wIOVmKxWuBy+VvrbZd1nomzCf8Cl4xqlvPV4Ue\nGV0NW9//sUyb9lJSGSJwJR+DJwtfSCc3lklTMG6glZIEL6EqwVbfxf1F3sKXFmo3\n1XTmqws0ltZtF1cmqcduIfUzlz/s3kHyb/Zr+j8CgYAX+ZibKovoSr/plyObhtck\nAxTJnvpUvRkpmfZWh1Ws0Aau5TzsJIV/tIf+/gxlkbdyrXBYf9DwLI0qR31MXV3Y\nelle64ej2d2zfj9F0ZQy0RAJyJYnG+6Rq84QI4My4AsEASzq9xaY64S9tHAKNz+d\nO47TOutlz3sJ1zShM/oPMQ==\n")
        
        credentials = ServiceAccountCredentials(
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
        selected_image = collection.median().clip(roi)  # Use median for a cleaner mosaic
        
        # Setup Map
        Map = geemap.Map(center=[(lat_ul + lat_lr) / 2, (lon_ul + lon_lr) / 2], zoom=8)
        
        # Visualization parameters (Sentinel-2 True Color example)
        vis_params = {}
        if satellite == "Sentinel-2":
            vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.4}
        elif satellite in ["Landsat-8", "Landsat-9"]:
            vis_params = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3}
        elif satellite == "MODIS":
            vis_params = {'bands': ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'], 'min': 0, 'max': 5000}
        
        Map.addLayer(selected_image, vis_params, f"{satellite} True Color")
        geojson = geemap.ee_to_geojson(roi)
        Map.add(geemap.folium.GeoJson(geojson, name="ROI"))
        
        # Display map
        Map.to_streamlit(height=600)
    else:
        st.error("No images found for the selected criteria.")
