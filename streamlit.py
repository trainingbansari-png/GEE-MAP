import streamlit as st
import ee
import geemap
import folium
from datetime import date
import json

# 1. MUST BE FIRST
st.set_page_config(layout="wide")

# 2. Earth Engine Initialization
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

    if count == 0:
        st.warning("No images found for the specified criteria.")
    else:
        # Take the median image for cleaner representation
        selected_image = collection.median().clip(roi)
        
        # Check if the selected image is valid (not None or empty)
        if selected_image is None:
            st.error("Selected image is invalid!")
            st.stop()
        
        # Visualize the image and check the values
        vis_params = {
            'bands': ['B4', 'B3', 'B2'],  # True color bands for Sentinel-2
            'min': 0, 
            'max': 3000, 
            'gamma': 1.4
        } if satellite == "Sentinel-2" else {}

        # Check if the image has the expected bands
        try:
            image_bands = selected_image.bandNames().getInfo()
            st.write(f"Image bands: {image_bands}")  # Display the bands to check if they match
        except Exception as e:
            st.write(f"Error reading bands: {e}")
        
        # Setup Map
        Map = geemap.Map(center=[(lat_ul + lat_lr) / 2, (lon_ul + lon_lr) / 2], zoom=8)
        
        # Add the layer
        try:
            Map.addLayer(selected_image, vis_params, f"{satellite} True Color")
            st.write("Image layer added to map")
        except Exception as e:
            st.error(f"Error adding image to map: {e}")
            st.stop()

        # Manually create the GeoJSON for the ROI (Rectangle)
        def create_geojson_from_roi(roi):
            coords = roi.coordinates().getInfo()[0]  # Extract coordinates of the rectangle
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coords]  # Coordinates for the polygon
                        },
                        "properties": {}
                    }
                ]
            }
            return geojson

        geojson = create_geojson_from_roi(roi)

        # Debugging: Print GeoJSON structure
        st.write(json.dumps(geojson, indent=2))  # Display GeoJSON structure

        # Ensure GeoJSON is valid
        if isinstance(geojson, dict) and "type" in geojson and "features" in geojson:
            try:
                # Add the ROI as a GeoJson object using geemap (correct method)
                Map.add_layer(folium.GeoJson(geojson, name="ROI"))
                st.write("GeoJSON layer added to map")
            except Exception as e:
                st.error(f"Error adding GeoJSON layer: {e}")
                st.stop()
        else:
            st.error("GeoJSON format is invalid.")
        
        # Display the map using the correct method for geemap
        try:
            Map.to_streamlit(height=600)  # This should render the map in Streamlit
            st.write("Map displayed successfully")
        except Exception as e:
            st.error(f"Error displaying map: {e}")
            st.stop()
