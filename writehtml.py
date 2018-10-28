"""module to write html files to s3"""
import mimetypes
import os
import pandas as pd
import boto3


class writedata:
    """create html and write to s3"""
    # pass in all_data from breakout function
    def write_file_to_s3(self, all_data):
        """create html and write to s3"""
        s3sr = boto3.resource('s3')
        # s3sc = boto3.client('s3')
        bucket = os.environ['BREAKOUT_BUCKETDATA_NAME']
        bucketobj = s3sr.Bucket(bucket)

        # parse entry/exits
        pdata = all_data['packageddata']
        trades = {'': ['1st Unit', '2nd Unit', '3rd Unit', '4th Unit'],
                  'Buy Stop': [pdata['Unit1'], pdata['Unit2'], pdata['Unit3'], pdata['Unit4']],
                  'Sell Stop1': [pdata['Stop1'], '', '', ''],
                  'Sell Stop2': [pdata['Stop1'], pdata['Stop2'], '', ''],
                  'Sell Stop3': [pdata['Stop1'], pdata['Stop2'], pdata['Stop3'], ''],
                  'Sell Stop4': [pdata['Stop1'], pdata['Stop2'], pdata['Stop3'], pdata['Stop4']]
                 }

        # create dataframe for easy transformatin to html
        df = pd.DataFrame.from_dict(trades)

        # change headings if breakout is low
        if all_data['direction'] == "low":
            df.columns = ['', 'Sell Stop', 'Buy Stop1', 'Buy Stop2', 'Buy Stop3', 'Buy Stop4']

        # writing file to s3 using the lamba temp directory and panda to_html function
        # table1_html = "/tmp/table1.html"
        # df.to_html(table1_html)

        # create the buy/sell html table for market
        table1_html = df.to_html(index=False, border=2)
        table1_html = table1_html.replace('<tr>', '<tr align="center">')

        # create second table of data relating to analysis
        table2_html = """<br></br>
                        Trading Day = %s
                        <br>Breakout Price = %s </br>
                        Tick = %s
                        <br>Breakout Days = %s </br>
                        Equity = %s
                        <br>Unit Size = %s </br>
                        ATR = %s
                        <br><a href="%s" target="_blank">%s</a></br>
                    """ %(all_data['tradingday'], all_data['breakoutprice'], all_data['packageddata']['tick'],
                          all_data['breakoutdays'], all_data['packageddata']['equity'],
                          all_data['packageddata']['unit_size'], all_data['packageddata']['atr'],
                          all_data['packageddata']['chart_url'],
                          all_data['symbol'] + "_" + all_data['direction'])

        # starting xml with styling the entry/exit table
        html_start = """<!DOCTYPE html>
                        <html lang="en" dir="ltr">
                          <head>
                            <meta charset="utf-8">
                            <title></title>
                            <style>
                                  table, th, td {
                                      border: 1px solid black;
                                      height: 22px;
                                      padding: 3px;
                                  }

                                  table {
                                      border-collapse: collapse;
                                      height: 20px;
                                  }
                                  </style>
                            </head>
                          <body>
                          <strong> %s nearing %s </strong><br></br>""" % (all_data['symbol'], all_data['direction'])

        # place a chart of the market in the html document
        html_chart = """<br></br><img class="chartimg" id="chartImg" src="%s">""" % (all_data['packageddata']['chart_url'])

        # closing html tags
        html_end = """</body></html>"""

        # put all the html pieces together
        html_conc = html_start + """<caption><b>%s</b></caption>
                                    <caption><b>%s</b></caption><br></br>
                                    %s """ % (table1_html, table2_html, html_chart) + html_end

        # name the file to be saved
        file_name = all_data['tradingday'] + '_' + all_data['symbol'] + '_' + all_data['breakoutdays'] + '_' + all_data['direction']+ ".html"

        # s3 key to store the file
        key = "htmlfiles/breakouts/" + file_name

        # write the html and store the file using lambda tmp directory
        file_name_path = "/tmp/" + file_name
        with open(file_name_path, 'w+') as file:
            file.write(html_conc)
            file.close()

        # using mimetypes
        content_type = mimetypes.guess_type(file_name)[0] or 'text/plain'
        # print(content_type)

        response = bucketobj.upload_file(str(file_name_path),
                                         str(key), ExtraArgs={'ContentType': content_type})

        # print(response)
