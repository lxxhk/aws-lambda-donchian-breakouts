"""create daily date file to process for breakouts - used in case I want to
    manually add multiple dates to the sns notification for breakout analysis"""

import os
import sys
from datetime import datetime
import mimetypes
import boto3

# client = boto3.client('lambda', region_name="us-east-1")
s3sr = boto3.resource('s3')
bucket = os.environ['BREAKOUT_BUCKETDATA_NAME']
bucketobj = s3sr.Bucket(bucket)
# this function will search s3 for current breakouts and send email (or text???)
# run this 15 minutes after running other lamda breakout funcitons
def send_datefile_to_s3(event, context):

    # create date with just today's dates
    # will run each weekday before breakouts analysis is run
    today_date_str = datetime.now().strftime("%Y-%m-%d")

    key = os.environ['BREAKOUT_SNS_DATE_KEY_NAME']
    path = "/tmp/"
    fullpath = path + key

    output = open(fullpath, "w")
    output.write(today_date_str)
    output.close()

    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    response = bucketobj.upload_file(str(fullpath),
                          str(key), ExtraArgs={'ContentType': content_type})
    # print(response)
