import json
import os
import boto3

client = boto3.client('lambda', region_name="us-east-1")
s3sr = boto3.resource('s3')
s3sc = boto3.client('s3')
bucket =  os.environ['BREAKOUT_BUCKETDATA_NAME']
key =  os.environ['BREAKOUT_SYMBOLS_KEY_NAME']
# Note: print command is logged in cloudwatch logs

# first function used to call another lambda function
# this function will be driven from a cron job nightly (watch UTC time zone???)
def trigger_breakout_lambdas(event, context):
    # read list of markets to analyze - file in s3 - read line by line
    obj = s3sr.Object(bucket, key)
    data = obj.get()['Body'].read().decode('utf-8')

    duration = data.splitlines()[0]
    maxRecords = data.splitlines()[1]
    market_list = data.splitlines()[2:]
    print(duration, maxRecords, market_list)

    invoked_function_name = os.environ['INVOKED_FUNCTION_NAME']

    # this lambda function invokes another lambda function
    for market in market_list:
        # print(market)
        # data transfered via Payload must be in json formatting
        # this passes one market at a time to a invoke a new lambda function
        data = {"market" : market, "maxRecords" : maxRecords, "type" : duration}
        # print(data)
        response = client.invoke(
            FunctionName=invoked_function_name,
            # InvocationType='RequestResponse', # synchornous - waits for response
            InvocationType='Event', # asynch - much faster - doesn't wait for response
            Payload=json.dumps(data)
        )

        # print(response)
        string_response = response["Payload"].read().decode('utf-8')

        #returns null if it works ok
        # parsed_response = json.loads(string_response)

        # print("Lambda invocation message:", parsed_response)
