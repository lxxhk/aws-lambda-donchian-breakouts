
import json
import os
import time
# from collections import namedtuple
import sys
import pandas as pd
# from ta import *
from ta import donchian_channel_hband, donchian_channel_lband, average_true_range
import requests
import boto3
from futuresdefinitions import futurespecs

# breakout lambda based on fixed 55 day breakout of donchian channels
# can make this more variable in the future (20 vs 55 vs ??)
dbtable = os.environ['BREAKOUT_DBTABLE_NAME']
dydbsc = boto3.client('dynamodb')
dydbsr = boto3.resource('dynamodb')
table = dydbsr.Table(dbtable)
item_data_dict = ''
entry_exit_dict = ''
root = ''
packaged_data = ''

# initialize object for getting futures specifications
cs = futurespecs()


def roundto(number, base, places):
    return round(base*round(number/base), places)


def get_entry_exit(direction, breakout_price):
    global entry_exit_dict, entry_exit_str, tick
    tick = float(cs.get_contract_info(root)[3])
    places = len(str(tick).split('.')[1])
    print(direction, breakout_price, tick, places)
    if direction == "high":
        Unit1 = roundto(breakout_price + tick, tick, places)
        Unit2 = Unit1 + roundto(0.5 * last_atr, tick, places)
        Unit3 = Unit2 + roundto(0.5 * last_atr, tick, places)
        Unit4 = Unit3 + roundto(0.5 * last_atr, tick, places)
        Stop1 = Unit1 - roundto(2.0 * last_atr, tick, places)
        Stop2 = Unit2 - roundto(2.0 * last_atr, tick, places)
        Stop3 = Unit3 - roundto(2.0 * last_atr, tick, places)
        Stop4 = Unit4 - roundto(2.0 * last_atr, tick, places)
    else:
        Unit1 = roundto(breakout_price - tick, tick, places)
        Unit2 = Unit1 - roundto(0.5 * last_atr, tick, places)
        Unit3 = Unit2 - roundto(0.5 * last_atr, tick, places)
        Unit4 = Unit3 - roundto(0.5 * last_atr, tick, places)
        Stop1 = Unit1 + roundto(2.0 * last_atr, tick, places)
        Stop2 = Unit2 + roundto(2.0 * last_atr, tick, places)
        Stop3 = Unit3 + roundto(2.0 * last_atr, tick, places)
        Stop4 = Unit4 + roundto(2.0 * last_atr, tick, places)

    # print(direction, breakout_price, tick, Unit1, places)
    entry_exit_str = """{
            "Unit1": "%s",
            "Unit2": "%s",
            "Unit3": "%s",
            "Unit4": "%s",
            "Stop1": "%s",
            "Stop2": "%s",
            "Stop3": "%s",
            "Stop4":" %s"
    }""" % (Unit1, Unit2, Unit3, Unit4, Stop1, Stop2, Stop3, Stop4)
    entry_exit_dict = json.loads(entry_exit_str)
    print(entry_exit_dict)
    return entry_exit_dict


def item_expiration(incr):
    time_increments_in_seconds = """{
        "plus_minute" : 60,
        "plus_hour" : 3600,
        "plus_day" : 86400,
        "plus_week" : 604800
    }"""
    time_increments_dict = json.loads(time_increments_in_seconds)
    epoch_time = int(time.time())
    expires = epoch_time + time_increments_dict[incr]
    return expires


def package_upload_data(direction):
    global packaged_data
    packaged_data = entry_exit_dict
    # print("packaged_data:", packaged_data)
    packaged_data['type'] = duration
    packaged_data['risk'] = str(url_payload['criteria']['risk'])
    packaged_data['min_volume'] = str(url_payload['criteria']['min_volume'])
    packaged_data['equity'] = str(url_payload['criteria']['equity'])
    packaged_data['breakout_days'] = str(url_payload['criteria']['breakout_days'])
    packaged_data['unit_size_cutoff'] = str(url_payload['criteria']['unit_size_cutoff'])
    packaged_data['direction'] = direction
    packaged_data['tradingDay'] = last_tradingDay
    packaged_data['symbol'] = symbol
    packaged_data['volume'] = str(last_volume)
    packaged_data['unit_size'] = str(unit_size)
    packaged_data['atr'] = str(last_atr)
    packaged_data['tick'] = str(tick)
    packaged_data['chart_url'] = chart_url
    # print(packaged_data)
    # print()
    # packaged_data = make_item(packaged_data)
    print(packaged_data)
    return packaged_data


def put_item_data(atrmultiple, direction, channel_price):
    global item_data_dict
    expires = item_expiration('plus_minute')
    item_data_str = """{
            "tradingday": "%s",
            "atrmultiple": "%s",
            "direction": "%s",
            "symbol": "%s",
            "breakoutprice": "%s",
            "ohlcv":
                {"open": "%s",
                "high": "%s",
                "low":" %s",
                "close": "%s",
                "volume": "%s"},
            "TTLExpiration": "%s",
            "breakoutdays" : "%s"
    }""" % (last_tradingDay, atrmultiple, direction, symbol, channel_price, last_open,
            last_high, last_low, last_close, last_volume, expires, breakout_days)
    item_data_dict = json.loads(item_data_str)
    item_data_dict['packageddata'] = packaged_data
    print("item_data_dict", item_data_dict)
    return item_data_dict


def getroot(symbol):
    global root
    if len(symbol) == 5:
        root = symbol[:2]
    elif len(symbol) == 4:
        root = symbol[:1]
    return root


def get_unit_size(risk, equity, last_atr, contract_size):
    unit_size = (risk / 2) * equity / last_atr / contract_size
    return unit_size


def make_item(data):
    """Changing float to string for dynamodb"""
    if isinstance(data, dict):
        return {k: make_item(v) for k, v in data.items()}
    if isinstance(data, list):
        return [make_item(v) for v in data]
    if isinstance(data, float):
        return str(data)
    return data

################################# LAMBDA HANDLER #########################################
def breakout_lambda(event, context):
    global last_don_lband, last_atr, last_open, last_high, last_low, last_close
    global last_tradingDay, symbol, last_volume, unit_size, breakout_days, url_payload, chart_url
    global duration

    # event is the json passed by the Payload parameter of the first lambda function
    # event example: {"market" : "ES*1", "maxRecords" : 100, "type" : "daily"}

    # log the event in cloudwatch to see json sent via first lambda function
    print(event)

    market = event['market']
    maxRecords = str(event['maxRecords'])
    duration = event['type']


    url_payload = {'criteria': {'min_volume': 400,
                                'risk': 2.0,
                                'equity': 25000,
                                'breakout_days': 20,
                                'unit_size_cutoff': 0.8}}

    min_volume = url_payload['criteria']['min_volume']
    risk = url_payload['criteria']['risk'] / 100
    breakout_days = url_payload['criteria']['breakout_days']
    equity = url_payload['criteria']['equity']
    unit_size_cutoff = url_payload['criteria']['unit_size_cutoff']

    url = 'https://marketdata.websol.barchart.com/getHistory.json?\
    apikey=020e9823c98a0753c62aacb0735a5226&symbol=' + market + '&type=' + duration + '&\
    startDate=20100101&maxRecords=' + maxRecords + '&order=asc'
    # print(url)

    myResponse = requests.get(url)
    # print(myResponse.text)
    data = json.loads(myResponse.text)
    if data['results'] is None:
        print(market, "no data")
        sys.exit()

    # print(data['results'][0]['symbol'])
    # print(data)

    # create data frame for pandas from results key in 'data'
    df = pd.DataFrame(data['results'])

    # check volume against criteria - exit if not met
    # **** USE VOLUME FROM PREVIOUS DAY - SOMETIMES LAST DAY'S VOLUME ISN'T AVAILABLE
    last_volume = df["volume"][len(df)-2]
    if last_volume < min_volume:
        print(market, "vol exit")
        sys.exit()

    # # get future's parameters
    # root = getroot(symbol)
    # # tick = float(get_root_info(root)[3])
    # contract_size = float(get_contract_info(root)[1])

    # get future's parameters
    symbol = data['results'][0]['symbol']
    root = getroot(symbol)
    print(root)

    # create chart url for analysis
    chart_url = "https://www.barchart.com/futures/quotes/" + symbol + "/interactive-chart"


    cs = futurespecs()
    # tick = float(cs.get_contract_info(root)[3])
    contract_size = float(cs.get_contract_info(root)[1])

    # get atr
    atr = average_true_range(df["high"], df["low"], df["close"], n=14, fillna=True)

    # get last atr
    last_atr = roundto(atr[len(atr)-1], 0.0000001, 7)
    unit_size = int(get_unit_size(risk, equity, last_atr, contract_size))
    # print("unit size: ", unit_size)

    # check the unit size cutoff and exit if not met
    if unit_size < unit_size_cutoff:
        print(market, "unitsize exit")
        sys.exit()

    # get the channels (breakout high and low prices)
    don_hband = donchian_channel_hband(df["close"], n=breakout_days, fillna=True)
    don_lband = donchian_channel_lband(df["close"], n=breakout_days, fillna=True)

    # get the last value
    last_don_lband = don_lband[len(don_lband)-1]
    last_don_hband = don_hband[len(don_hband)-1]
    last_open = df["open"][len(df)-1]
    last_high = df["high"][len(df)-1]
    last_low = df["low"][len(df)-1]
    last_close = df["close"][len(df)-1]
    last_tradingDay = df["tradingDay"][len(df)-1]

    # calculate atr multiples
    delta_from_high = last_don_hband - last_high
    delta_from_low = last_low - last_don_lband
    atr_multiple_high = roundto(delta_from_high / last_atr, 0.00001, 5)
    atr_multiple_low = roundto(delta_from_low / last_atr, 0.00001, 5)


    if 0 <= atr_multiple_high <= 5:
        # print("Nearing High ATR Mulitple: {:.2f}".format(atr_multiple_high))
        #create json for dynamodb put_item
        direction = "high"
        get_entry_exit(direction, last_don_hband)
        package_upload_data(direction)
        put_item_data(atr_multiple_high, direction, last_don_hband)
        # print(item_data_dict)
        response = table.put_item(Item=item_data_dict)
        print(response)
        # print('\n' *2)

    if 0 <= atr_multiple_low <= 5:
        # print("Nearing Low ATR Multiple: {:.2f}".format(atr_multiple_low))
        direction = "low"
        get_entry_exit(direction, last_don_lband)
        package_upload_data(direction)
        put_item_data(atr_multiple_low, direction, last_don_lband)
        # print(item_data_dict)
        response = table.put_item(Item=item_data_dict)
        print(response)
