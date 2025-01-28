import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session
import json
import concurrent.futures
import time

def invoke_api_gateway_signed(url, payload, region):
    # Setup the AWS session and credentials
    session = Session()
    credentials = session.get_credentials()

    # Ensure credentials are present
    if credentials is None:
        return None, "No valid AWS credentials found."

    # Create AWSRequest object
    request = AWSRequest(method='POST', url=url, data=json.dumps(payload))

    # Sign the request using SigV4Auth
    signer = SigV4Auth(credentials, 'execute-api', region)
    signer.add_auth(request)

    # Extract signed headers
    headers = dict(request.headers.items())

    try:
        # Make the HTTP POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)

def invoke_concurrently(api_gateway_url, payload, num_invocations, duration, region):
    interval = duration / num_invocations
    futures = []

    # Use ThreadPoolExecutor to handle concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        start_time = time.time()

        for _ in range(num_invocations):
            time_elapsed = time.time() - start_time
            # Ensure we maintain the correct invocation interval
            if time_elapsed < duration:
                futures.append(executor.submit(invoke_api_gateway_signed, api_gateway_url, payload, region))
                time.sleep(max(0, interval - (time.time() - start_time)))
                start_time = time.time()
        
        # Process the future results
        for future in concurrent.futures.as_completed(futures):
            status, response = future.result()
            if status:
                print(f'Status: {status}, Response: {response}')
            else:
                print(f'Error invoking API: {response}')

if __name__ == "__main__":
    api_gateway_url = 'api-url'  # Replace with your API Gateway URL
    payload = {"key": "value"}  # Define your JSON payload
    region = 'us-east-1'
    num_invocations = 1000
    duration = 8  # In seconds

    invoke_concurrently(api_gateway_url, payload, num_invocations, duration, region)