"""Send text messaging to subscribed SNS topic"""
import os, sys
import json
from datetime import datetime
import boto3

# client = boto3.client('lambda', region_name="us-east-1")
s3sr = boto3.resource('s3')
# s3sc = boto3.client('s3')
snssc = boto3.client('sns')

bucket = os.environ['BREAKOUT_BUCKETDATA_NAME']
breakout_topic_arn = os.environ['BREAKOUT_TOPIC_ARN']
phonenumber = os.environ['BREAKOUT_PHONE_NUMBER']
key = os.environ['BREAKOUT_SNS_DATE_KEY_NAME']

# this function will search s3 for current breakouts and send email (or text???)
# run this 15 minutes after running other lamda breakout funcitons

def send_breakout_notifications(event, context):
    # read list of markets to analyze - file in s3 - read line by line
    obj = s3sr.Object(bucket, key)
    data = obj.get()['Body'].read().decode('utf-8')

    sns_dates = data.splitlines()

    for sns_date in sns_dates:
        # bucket url
        base_url = 'https://s3.amazonaws.com/' + bucket + '/'
        today_date_str = sns_date
        # today_date_str = datetime.now().strftime("%Y-%m-%d")
        # for testing may need to hardcode datestring
        # today_date_str = '2018-11-12'

        # specific prefixes for breakouts files
        prefix = 'htmlfiles/breakouts'

        # limit to prefix
        paginator = s3sr.meta.client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket,
                                           Prefix=prefix,
                                           PaginationConfig={'MaxItems': 1000})

        # create list of html file urls for json messaging in emails
        # only for current day's files based on date in key name
        for page in page_iterator:
            # if page['KeyCount'] == 0:  ## this also works
            if page.get('Contents') is None:
                # print(page.get('Contents'))
                # print("no files today")
                keyurl_list = ['no files', 'today']
                response = snssc.publish(
                    PhoneNumber=phonenumber,
                    Message="No breakouts to review"
                    )
                sys.exit()
            else:
                # parsing out date to get current breakout htmls
                keyurl_list = [base_url + obj['Key'] for obj in page.get('Contents') if obj['Key'].split('/')[-1].split('_')[0] == today_date_str]

            print(keyurl_list)

            # use \\n to escape line break
            keyurl_str = '\\n\\n'.join(keyurl_list)
            keyurl_str = "Breakouts to review:\\n\\n" + keyurl_str + "\\n"
            # print(keyurl_str)

            # using json format as messaging is differnent for each protocol
            message = """{
                    "default": "Nothing to report",
                    "email": "%s",
                    "sms": "new markets to check out: %s"
                    }""" % (keyurl_str, str(len(keyurl_list)))

            # make it json format
            mm = json.loads(message)

            # subject line for email
            subject = today_date_str + ' - ' + str(len(keyurl_list)) + ' breakouts to review'

            # publish to topic, then each subscriber gets the email
            response = snssc.publish(
                TopicArn=breakout_topic_arn,
                # TargetArn='string',
                Message=json.dumps(mm),
                Subject=subject,
                MessageStructure='json'
            )
