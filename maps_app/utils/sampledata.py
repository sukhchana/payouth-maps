import random

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
        "latlng": f"{new_lat},{new_lng}",
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
