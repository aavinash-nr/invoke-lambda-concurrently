import boto3
import concurrent.futures
import time

# Initialize Lambda client
lambda_client = boto3.client('lambda')

# Lambda function name and payload
function_name = 'function arn'

payload = b'{"error":1}'  # Modify this based on your Lambda function's input

# Total invocations and the time window (3 minutes = 180 seconds)
# this will try to trigger lambda 30 times in 3 seconds
total_invocations = 30
time_window = 3 

# Function to invoke Lambda
def invoke_lambda(i):
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Change to 'Event' for asynchronous invocation
            Payload=payload
        )
        print(f"Invocation {i}: {response['StatusCode']}")
    except Exception as e:
        print(f"Error invoking Lambda {i}: {e}")

# Parallel execution using ThreadPoolExecutor
def invoke_in_parallel():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        start_time = time.time()
        # Attempt to control the invocation rate by spreading them evenly over the time window
        for i in range(total_invocations):
            futures.append(executor.submit(invoke_lambda, i))
            time_to_wait = (i / total_invocations) * time_window - (time.time() - start_time)
            if time_to_wait > 0:
                time.sleep(time_to_wait)
        concurrent.futures.wait(futures)

# Run the invocations
invoke_in_parallel()