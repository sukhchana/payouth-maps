import logging
import random
import hashlib
import sys
from flask import Flask, render_template, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_cors import cross_origin

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

random.seed = 10


def generate_locations(num, lat=40.4406, lng=-79.9959, current_count=0, locations=[]):
    if current_count == num:
        return locations
    # PA_bounds = {"north": 42.3, "south": 39.7, "west": -80.5, "east": -74.7}

    # Adjust the latitude and longitude slightly for each subsequent location
    new_lat = random.randint(40, 41) + random.random()
    new_lng = (random.randrange(77, 80) + random.random()).__neg__()

    # Mock address and name for the location
    address_num = random.randint(100, 999)
    city_names = [
        "Pittsburgh",
        "Philadelphia",
        "Harrisburg",
        "Lancaster",
        "Allentown",
        "Erie",
        "Scranton",
        "Bethlehem",
        "State College",
        "York",
        "Reading",
        "Altoona",
        "Wilkes-Barre",
        "Easton",
        "Lebanon",
        "Hazleton",
        "Chambersburg",
        "Pottsville",
        "Carlisle",
        "Hanover",
        "Williamsport",
        "Sharon",
        "Hermitage",
        "Greensburg",
        "New Castle",
        "Johnstown",
        "McKeesport",
        "Norristown",
        "Chester",
        "Bethel Park",
        "Monroeville",
        "Plum",
        "Doylestown",
        "Meadville",
        "Indiana",
        "St. Marys",
    ]
    street_names = [
        "Liberty",
        "Broad",
        "Penn",
        "Main",
        "Hamilton",
        "College",
        "Lakefront",
        "King",
        "Capitol",
        "Market",
    ]
    street_types = ["St", "Ave", "Dr", "Rd", "Blvd"]
    city = random.choice(city_names)
    street_name = random.choice(street_names)
    zip_code = random.randint(15001, 19640)
    address = f"{address_num} {street_name} {random.choice(street_types)}, {city}, PA {zip_code}"
    name = f"{city} Voting Center"

    location = {
        "latlng": f"{new_lat},{new_lng,}",
        "lat": new_lat,
        "lng": new_lng,
        "name": name,
        "city": city,
        "state": "PA",
        "address": address,
        "zip": zip_code,
    }

    locations.append(location)

    return generate_locations(num, new_lat, new_lng, current_count + 1, locations)


voting_locations = generate_locations(15)


@app.route("/")
@cross_origin(origins=["*"])
def index():
    """
    Renders a google map with polling locations retreieved from a dynamodb table
    Returns:
    - Rendered HTML.
    """
    mymap = Map(
        identifier="view-side",
        lat=40.2732,  # Central latitude for Pennsylvania
        lng=-76.8867,  # Central longitude for Pennsylvania
        fit_markers_to_bounds=True,
        style="height:600px;width:100%;margin:0;",
        markers=get_polling_stations("pollinglocation"),
    )

    return render_template(
        "index.html",
        mymap=mymap,
        google_maps=google_maps,
        voting_locations=voting_locations,
    )


@app.route("/json")
def html_data():
    """
    Raw HTML from JSON.
    Returns:
    - Rendered HTML in json format
    """
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
