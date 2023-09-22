from decimal import Decimal
import logging
import json
import hashlib
import sys
from flask import Flask, render_template, jsonify, request
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_cors import cross_origin
from flask import Flask, render_template
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np



from maps_app.utils.get_secrets import get_secret
from maps_app.utils.get_dynamodb import get_polling_stations, write_to_dynamodb


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
    # df_pa = pd.read_excel(file_path, sheet_name=sheet_name)
    with open("./mapS_app/county-data.json", "r") as f:
        geojson = json.load(f)
    with open("./mapS_app/df_pa.json", "r") as f:
        df_pa = pd.DataFrame(json.load(f))
    
    
    county_data = [
        {
            "fips": feature["properties"]["STATE"] + feature["properties"]["COUNTY"],
            "County": feature["properties"]["NAME"].upper(),
        }
        for feature in geojson["features"]
        if feature["properties"]["STATE"] == "42"
    ]

    df_fips = pd.DataFrame(county_data)

    merged_df = pd.merge(df_pa, df_fips, on="County", how="left")

    merged_df["population"] = np.log(merged_df["18 to 24"] + 1)

    fig = px.choropleth_mapbox(
        merged_df,
        geojson=geojson,
        locations="fips",
        color="population",  # Use the logarithmic column for coloring
        hover_name="County",
        hover_data={"18 to 24": True, "population": False, "fips": False},
        mapbox_style="carto-positron",
        color_continuous_scale="Viridis",
        title="Population of Pennsylvania Counties (Age Group: 18 to 24) - Log Scale",
        center={"lat": 40.994593, "lon": -77.604698},  # Center of PA
        zoom=5,
    )

    # Display the map

    fig.update_layout(
        autosize=True,
        height=600,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar=dict(len=0.75, x=0.5, y=-0.1, orientation="h", thickness=15),
    )

    plot_html = pio.to_html(
        fig,
        full_html=False,
    )

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


@app.route("/update_dynamodb/<param_value>", methods=["POST"])
def update_dynamodb(table_name="pollinglocation"):
    data = request.json
    key = data["key"]
    del data["key"]
    if key != "admin":
        return jsonify({"status_code": 400})
    response_list = []

    if table_name == "pollinglocation":
        for item in data["data"]:
            # Ensure lat and lng are Decimals
            item["lat"] = Decimal(str(item["lat"]))
            item["lng"] = Decimal(str(item["lng"]))
            response = write_to_dynamodb(table_name, item)
            response_list.append(response)
        return jsonify(response_list)
    else:
        for item in data["data"]:
            response = write_to_dynamodb(table_name, item)
            response_list.append(response)
        return jsonify(response_list)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=443)
