import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name="GoogleMapsAPI", region_name="us-east-1"):
    """
    Retreives the specified secret from a given region.

    Parameters:
    - secret_name: Name of the secret.
    - region_name: AWS region.

    Returns:
    - secret value
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:

        raise e
    
    secret = get_secret_value_response["SecretString"]

    return secret

if __name__ == "__main__":
    print(get_secret())