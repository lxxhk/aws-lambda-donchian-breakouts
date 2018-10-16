
import mimetypes
import os
import pandas as pd
import boto3


class writedata:

    def write_file_to_s3(self, all_data):
        """using temp directory in lambda to store and then write to s3"""
        s3sr = boto3.resource('s3')
        s3sc = boto3.client('s3')
        bucket = os.environ['BREAKOUT_BUCKETDATA_NAME']
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

        # table1_html = "/tmp/table1.html"
        # df.to_html(table1_html)
        table1_html = df.to_html(index=False, border=2)
        table1_html = table1_html.replace('<tr>', '<tr align="center">')

        # new data set to add to second html file
        trade_info = {}
        trade_info['tradingday'] = all_data['tradingday']
        trade_info['direction'] = all_data['direction']
        trade_info['symbol'] = all_data['symbol']
        trade_info['breakoutprice'] = all_data['breakoutprice']
        trade_info['breakoutdays'] = all_data['breakoutdays']
        trade_info['equity'] = all_data['packageddata']['equity']
        trade_info['tick'] = all_data['packageddata']['tick']
        trade_info['unitsize'] = all_data['packageddata']['unit_size']
        trade_info['charturl'] = all_data['packageddata']['chart_url']
        # print(trade_info)

        df_info = pd.DataFrame(list(trade_info.items()))
        df_info.columns = ["Item", "Value"]

        # table2_html = "/tmp/table2.html"
        # df_info.to_html(table2_html)

        table2_html = df_info.to_html(index=False, border=1)

        html_conc = """<br></br><caption><b>%s</b></caption><br></br>
                        <br></br><caption><b>%s</b></caption><br></br>""" % (table1_html, table2_html)

        file_name = pdata['tradingDay'] + '_' + pdata['symbol'] + '_' + pdata['direction'] + ".html"
        key = "htmlfiles/" + file_name

        file_name_path = "/tmp/" + file_name
        with open(file_name_path, 'w+') as file:
            file.write(html_conc)
            file.close()

        # using mimetypes
        content_type = mimetypes.guess_type(file_name)[0] or 'text/plain'
        # print(content_type)

        response = bucketobj.upload_file(str(file_name_path),
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
