
import mimetypes
import os
import pandas as pd
import boto3


class writedata:

    def write_file_to_s3(self, all_data):
        """using temp directory in lambda to store and then write to s3"""
        s3sr = boto3.resource('s3')
        s3sc = boto3.client('s3')
        bucket =  os.environ['BREAKOUT_BUCKETDATA_NAME']
        bucketobj = s3sr.Bucket(bucket)

        pdata = all_data['packageddata']
        trades = {'': ['1st Unit', '2nd Unit', '3rd Unit', '4th Unit'],
                  'Buy Stop': [pdata['Unit1'], pdata['Unit2'], pdata['Unit3'], pdata['Unit4']],
                  'Sell Stop1': [pdata['Stop1'], '', '', ''],
                  'Sell Stop2': [pdata['Stop1'], pdata['Stop2'], '', ''],
                  'Sell Stop3': [pdata['Stop1'], pdata['Stop2'], pdata['Stop3'], ''],
                  'Sell Stop4': [pdata['Stop1'], pdata['Stop2'], pdata['Stop3'], pdata['Stop4']]
                 }

        df = pd.DataFrame.from_dict(trades)
        if all_data['direction'] == "low":
            df.columns = ['', 'Sell Stop', 'Buy Stop1', 'Buy Stop2', 'Buy Stop3', 'Buy Stop4']

        # writing file to s3 using the lamba temp directory and panda to_html function
        file_name = pdata['tradingDay'] + pdata['symbol'] + pdata['direction'] + ".html"
        lambda_path = "/tmp/" + file_name
        key = "htmlfiles/" + file_name

        df.to_html(lambda_path)

        # using mimetypes
        content_type = mimetypes.guess_type(file_name)[0] or 'text/plain'
        # print(content_type)

        response = bucketobj.upload_file(str(lambda_path),
                                         str(key), ExtraArgs={'ContentType': content_type})

        print(response)

        # --------------------------------------------------------------------------------
        # writing file to s3 using the lamba temp directory and open file method
        # not used but works
        # file_name = pdata['tradingDay'] + pdata['symbol'] + pdata['direction'] + ".json"
        # lambda_path = "/tmp/" + file_name
        # key = "jsonfiles/" + file_name
        #
        # with open(lambda_path, 'w+') as file:
        #     file.write(str(all_data))
        #     file.close()
        #
        # response = bucketobj.upload_file(str(lambda_path),
        #                                  str(key), ExtraArgs={'ContentType': content_type})
        #
        # print(response)
