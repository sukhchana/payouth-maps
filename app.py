import logging
import hashlib
import sys
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from maps_app.utils.get_secrets import get_secret


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

secret_value = get_secret(secret_name="GoogleMapsAPI", region_name="us-east-1")
# app.config['GOOGLEMAPS_KEY'] = secret_value
secret_hash = hashlib.md5(secret_value.encode()).hexdigest()

# Initialize the extension
google_maps = GoogleMaps(app)
google_maps.key = secret_value
print("google_maps.key")
print(secret_value)
print("google_maps.key")
@app.route('/')
def index():
    # Creating a map in the view
    # You can set key as config
    
    app.logger.info(f"secret from secrets manager hash:{secret_hash}")
    print(f"secret from secrets manager hash:{secret_hash}")

    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    return render_template('index.html', mymap=mymap, google_maps=google_maps)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
