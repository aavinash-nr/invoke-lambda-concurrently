import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session
import concurrent.futures
import time
import json

def invoke_api_gateway_signed(url, payload, region):
    session = Session()  # Create a session
    credentials = session.get_credentials()  # Fetch the credentials
    request = AWSRequest(method='POST', url=url, data=json.dumps(payload))

    # AWSSignatureV4 signing process
    signer = SigV4Auth(credentials, 'execute-api', region)
    signer.add_auth(request)

    # Extract headers from the signed request and send the POST request
    headers = dict(request.headers.items())

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)

def controlled_invocation(api_gateway_url, payload, num_invocations, duration, region):
    interval = duration / num_invocations

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        start_time = time.time()

        for _ in range(num_invocations):
            futures.append(executor.submit(invoke_api_gateway_signed, api_gateway_url, payload, region))
            time_elapsed = time.time() - start_time
            time.sleep(max(0, interval - time_elapsed))
            start_time = time.time()

        for future in concurrent.futures.as_completed(futures):
            status, response = future.result()
            print(f'Status: {status}, Response: {response}')

if __name__ == "__main__":
    api_gateway_url = 'api_gateway_url'  # e.g., 'https://your-api-id.execute-api.us-west-2.amazonaws.com/Prod/your-resource'

    payload = {"key": "value"}  # Adjust the payload as necessary
    num_invocations =1
    duration = 1 # seconds
    region = 'us-east-1'  # e.g., 'us-west-2'

    start_time = time.time()
    controlled_invocation(api_gateway_url, payload, num_invocations, duration, region)
    end_time = time.time()

    print(f'Total time for {num_invocations} invocations: {end_time - start_time} seconds')