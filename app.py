import logging
import json
import hashlib
import sys
from flask import Flask, render_template, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_cors import cross_origin
from flask import Flask, render_template
import plotly.express as px
import plotly.io as pio
import pandas as pd


from maps_app.utils.get_secrets import get_secret
from maps_app.utils.get_dynamodb import get_polling_stations


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

secret_value = get_secret(secret_name="GoogleMapsAPI", region_name="us-east-1")
app.config["GOOGLEMAPS_KEY"] = secret_value
secret_hash = hashlib.md5(secret_value.encode()).hexdigest()

app.logger.info(f"secret from secrets manager hash:{secret_hash}")

# Initialize the extension
google_maps = GoogleMaps(app)


@app.route("/")
@cross_origin(origins=["*"])
def index():
    """
    Renders a google map with polling locations retreieved from a dynamodb table
    Returns:
    - Rendered HTML.
    """
    voting_locations = get_polling_stations("pollinglocation")
    mymap = Map(
        identifier="view-side",
        lat=40.2732,  # Central latitude for Pennsylvania
        lng=-76.8867,  # Central longitude for Pennsylvania
        fit_markers_to_bounds=True,
        style="height:600px;width:100%;margin:0;",
        markers=voting_locations,
    )

    return render_template(
        "index.html",
        mymap=mymap,
        google_maps=google_maps,
        voting_locations=voting_locations,
    )


@app.route("/county_map")
@cross_origin(origins=["*"])
def county_maps_page():
    # Load the specific sheet from the Excel file
    file_path = "./currentvotestats.xls"
    sheet_name = "All by Age"
    df_pa = pd.read_excel(file_path, sheet_name=sheet_name)

    print(df_pa)
    # Fetch the geojson
    with open("./county-data.json") as f:
        geojson = json.load(f)

    # Extract FIPS codes and county names from the geojson
    county_data = [
        {
            "fips": feature["properties"]["STATE"] + feature["properties"]["COUNTY"],
            "County": feature["properties"][
                "NAME"
            ].upper(),  # Convert to uppercase to match your dataframe
        }
        for feature in geojson["features"]
        if feature["properties"]["STATE"] == "42"
    ]

    df_fips = pd.DataFrame(county_data)

    merged_df = pd.merge(df_pa, df_fips, on="County", how="left")

    import numpy as np

    merged_df["log_pop"] = np.log(
        merged_df["18 to 24"] + 1
    )  # Adding 1 to handle counties with 0 population in the age group

    fig = px.choropleth_mapbox(
        merged_df,
        geojson=geojson,
        locations="fips",
        color="log_pop",  # Use the logarithmic column for coloring
        hover_name="County",
        hover_data={"18 to 24": True, "log_pop": False, "fips": False},
        mapbox_style="carto-positron",
        color_continuous_scale="Viridis",
        title="Population of Pennsylvania Counties (Age Group: 18 to 24) - Log Scale",
        center={"lat": 40.994593, "lon": -77.604698},  # Center of PA
        zoom=6,
    )
    # Adjust the layout
    fig.update_layout(height=600, autosize=True)  # You can modify the height value as needed

    # Display the map
    print(fig._config)

    plot_html = pio.to_html(fig, full_html=False)

    return render_template("county_map.html", plot_html=plot_html)


@app.route("/json")
def html_data():
    """
    Raw HTML from JSON.
    Returns:
    - Rendered HTML in json format
    """
    voting_locations = get_polling_stations("pollinglocation")
    mymap = Map(
        identifier="view-side",
        lat=40.2732,  # Central latitude for Pennsylvania
        lng=-76.8867,  # Central longitude for Pennsylvania
        fit_markers_to_bounds=True,
        style="height:600px;width:100%;margin:0;",
        markers=voting_locations,
    )

    rendered_html = render_template(
        "index.html",
        mymap=mymap,
        google_maps=google_maps,
        voting_locations=voting_locations,
    )
    return jsonify(data=rendered_html), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=443)
