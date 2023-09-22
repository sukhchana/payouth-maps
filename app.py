import logging
import random
import hashlib
import sys
from flask import Flask, render_template, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from flask_cors import cross_origin

from maps_app.utils.get_secrets import get_secret


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
    address = f"{address_num} {random.choice(street_names)} {random.choice(street_types)}, {city}, PA {random.randint(15001, 19640)}"
    name = f"{city} Voting Center"

    location = {
        "lat": new_lat,
        "lng": new_lng,
        "infobox": f"<b>{name}</b><br>{address}",
    }
    locations.append(location)

    return generate_locations(num, new_lat, new_lng, current_count + 1, locations)


voting_locations = generate_locations(15)


@app.route("/")
@cross_origin(origins=["*"])
def index():
    mymap = Map(
        identifier="view-side",
        lat=40.2732,  # Central latitude for Pennsylvania
        lng=-76.8867,  # Central longitude for Pennsylvania
        fit_markers_to_bounds=True,
        style="height:600px;width:100%;margin:0;",
        markers=voting_locations,
    )

    geometry = f'<script src="https://maps.googleapis.com/maps/api/js?key={secret_value}&libraries=geometry"></script>'


    location_script = """function user_loc() {
    return new Promise(function(resolve, reject) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;
                console.log(lat, lng);
                resolve(new google.maps.LatLng(lat, lng));
            }, function(error) {
                reject(error);
            });
        } else {
            reject(new Error("Geolocation is not supported by this browser."));
        }
    });
}
let userLatitude, userLongitude;

user_loc()
    .then(location => {
        userLatitude = location.lat;
        userLongitude = location.lng;
        console.log(userLatitude, userLongitude);
    })
    .catch(error => {
        console.error(error.message);
    });

"""

    tmp_html = render_template(
        "index.html",
        mymap=mymap,
        google_maps=google_maps,
        voting_locations=voting_locations,
    )
    fixed_html = tmp_html.replace(
        f'<script src="//maps.googleapis.com/maps/api/js?key={secret_value}&language=en&region=US" type="text/javascript"></script>',
       geometry,
    )
    fixed_html = fixed_html.replace(
        "var prev_infowindow_map = null;",
        "var prev_infowindow_map = null;\n" + location_script,
    )
    fixed_html = fixed_html.replace(
        "center: new google.maps.LatLng(40.2732, -76.8867),", "center: (userLatitude, userLongitude),"
    )

    return fixed_html


@app.route("/json")
def html_data():
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
