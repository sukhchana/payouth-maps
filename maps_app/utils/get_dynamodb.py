from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

from maps_app.utils.sampledata import voting_locations


def get_polling_stations(table_name):
    """
    Reads all items for the specified DynamoDB table.

    Parameters:
    - table_name: Name of the DynamoDB table.

    Returns:
    - The response from the DynamoDB service.
    """
    session = boto3.Session()
    dynamodb = session.resource("dynamodb")

    # Initialize table resource
    table = dynamodb.Table(table_name)

    # Use the scan method to fetch all records
    try:
        response = table.scan()
        items = [
            {
                "lat": item["lat"],
                "lng": item["lng"],
                "infobox": f"<b>{item['name']}</b><br>{item['address']}",
            }
            for item in response["Items"]
        ]
        return items
    except:
        return []


def write_to_dynamodb(table_name, item):
    """
    Writes an item to the specified DynamoDB table.

    Parameters:
    - table_name: Name of the DynamoDB table.
    - item: Dictionary containing the item data to be written.

    Returns:
    - The response from the DynamoDB service.
    """

    # Initialize a session using Amazon DynamoDB
    session = boto3.Session()
    dynamodb = session.resource("dynamodb")

    # Initialize table resource
    table = dynamodb.Table(table_name)

    # Write the item to the table
    response = table.put_item(Item=item)

    return response


if __name__ == "__main__":
    # Example usage
    table_name = "pollinglocation"
    # items = get_polling_stations(table_name)
    # for item in items:
    #     print(item)

    items = voting_locations
    for item_data in items:
        item_data["lat"] = Decimal(str(item_data["lat"]))
        item_data["lng"] = Decimal(str(item_data["lng"]))
        response = write_to_dynamodb(table_name, item_data)
        print(response)
