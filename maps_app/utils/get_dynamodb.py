import boto3
from botocore.exceptions import ClientError


def get_polling_stations(table_name):
    # Initialize a session using Amazon DynamoDB
    session = boto3.Session()
    dynamodb = session.resource("dynamodb")

    # Initialize table resource
    table = dynamodb.Table(table_name)

    # Use the scan method to fetch all records
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


if __name__ == "__main__":
    # Example usage
    table_name = "pollinglocation"
    items = get_polling_stations(table_name)
    for item in items:
        print(item)
