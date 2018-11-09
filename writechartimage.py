"""module to download and write chart images to s3"""

import mimetypes
import urllib.request
import re
import os
import boto3

class writeimage:
    """module to download and write chart images to s3"""

    def download_and_write_file_to_s3(self, symbol):
        """using temp directory in lambda to store and then write to s3"""

        bucket = os.environ['BREAKOUT_BUCKETDATA_NAME']
        print(bucket)
        s3sr = boto3.resource('s3')
        # s3sc = boto3.client('s3')

        bucketobj = s3sr.Bucket(bucket)

        # url to get html source code to pull chart image url
        # symbol = 'CZ18'
        url = 'https://stockcharts.com/h-sc/ui?s=^' + symbol
        print(url)
        # site uses cookies, need to pass user-agent in header
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent':user_agent}
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)

        # data is binary
        data = response.read().decode('UTF-8')

        # find the starting point of the image string
        start_pos = re.search(r'id="chartImg" src="/', data)
        start_pos = start_pos.end()
        new_str = data[start_pos - 1:start_pos + 500]
        # find the end of the image string based on closing '>'
        img_src = new_str[:new_str.find(">") - 3]
        img_url = 'https:' + img_src
        print(img_url)
        # file to be saved locally, then uploaded to s3
        fn = symbol + '.jpg'
        path = "/tmp/"
        fullpath = path + fn
        request = urllib.request.Request(img_url, None, headers)
        response = urllib.request.urlopen(request)
        output = open(fullpath, "wb")
        output.write(response.read())
        output.close()

        # key and file name to be saved in s3
        key = "chartimages/" + fn

        content_type = mimetypes.guess_type(fn)[0] or 'text/plain'
        response = bucketobj.upload_file(str(fullpath),
                              str(key), ExtraArgs={'ContentType': content_type})
        print(response)
