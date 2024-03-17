import json,re
import pandas as pd
import  matplotlib.pyplot as plt
from datetime import datetime
import pytz
import base64

# helper functions
def findHeader(req,headertype,headername,op = None):
    value = "None"
    if headertype == 'response':
        for h in req['response']['headers']:
            if op == 'in':
                if headername in h['name']:
                    value = h['value']
                    break
            else:
                if headername == h['name']:
                    value = h['value']
                    
                    break
    if headertype == 'cdn-timing':
        value = 0
        for h in req['response']['headers']:
            if op == 'eq':
                if 'server-timing' in h['name']:
                    if headername in h['value']:
                        
                        value = int(h['value'].split(';')[1].split('=')[1])
                        break
        if value is None:
            return 0
    return value

#------------------------------------------------------------------------------------------------
def convertDateTime(startedDateTime):
    # Convert string to datetime object
    utc_startedDateTime = datetime.strptime(startedDateTime, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Define UTC timezone
    utc_timezone = pytz.utc

    # Convert UTC time to Indian Standard Time (IST)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    ist_time = utc_startedDateTime.replace(tzinfo=utc_timezone).astimezone(ist_timezone)

    # Format the IST time as per your requirement
    ist_formatted_startedDateTime = ist_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return ist_formatted_startedDateTime

#------------------------------------------------------------------------------------------------

def analyze_url(url):

    #check the API type
    apiType = url.split("//")[1].split(".")[0]

    # Check if the url contains "/cmots/"
    isCmotsApi = 'Y' if "/cmots/" in url else 'N'

    # Check if the url contains "/equity/"
    isEquity = 'Y' if "/equity/" in url else 'N'

    # Check if the url contains "/commodity/"
    isCommodity = 'Y' if "/commodity/" in url else 'N'

   # Check if the url contains "/stock-detailed/"
    isStockDetailed = 'Y' if "/stock-detailed/" in url else 'N'

    # Check if the url contains "/TradingViewData_AllAssetNew/"
    isTradingViewData = 'Y' if "/TradingViewData_AllAssetNew/" in url else 'N'

    # Check if the url contains "/1newserviceapi/"
    is1newserviceApi = 'Y' if "/1newserviceapi/" in url else 'N'

    # Check if the url contains "/60newserviceapi/"
    is60newserviceApi = 'Y' if "/60newserviceapi/" in url else 'N'

    # Extract the last part of the URL after splitting by "/"
    parts = url.split("/")
    last_part = parts[-1]

    # Check if "TradingViewData_AllAssetNew" is present in the URL and extract the last part after splitting by "/"
    encrypted_part = None
    if "TradingViewData_AllAssetNew" in url:
        encrypted_part = last_part

    # Decode the base64-encoded string
    decoded_value = None
    if encrypted_part:
        decoded_bytes = base64.b64decode(encrypted_part)
        decoded_value = decoded_bytes.decode("utf-8") 
    else:
        decoded_value = "N"

    return apiType, isCmotsApi, isEquity,isCommodity, isStockDetailed, isTradingViewData ,is1newserviceApi, is60newserviceApi, decoded_value

#------------------------------------------------------------------------------------------------

## parsing the decoded values
def extract_variables(decoded_string):

    if decoded_string == "N":
        return tuple("N" for _ in range(11))  # Return tuple of "N" for all variables

    # Parse the JSON string
    decoded_object = json.loads(decoded_string)

    # Extract variables
    cc_code = decoded_object.get("co_code", "")
    exchange = decoded_object.get("exchange", "")
    from_date = decoded_object.get("fromdate", "")
    to_date = decoded_object.get("todate", "")
    interval = decoded_object.get("interval", "")
    asset = decoded_object.get("Asset", "")
    symbol = decoded_object.get("Symbol", "")
    expiry_date = decoded_object.get("expirydate", "")
    strike_price = decoded_object.get("strikeprice", "")
    strike_price_point = decoded_object.get("strikepricepoint", "")
    option = decoded_object.get("option", "")

    return cc_code, exchange, from_date, to_date, interval, asset, symbol, expiry_date, strike_price, strike_price_point, option

#------------------------------------------------------------------------------------------------
def check_for_response_trade_data(response):
    has_response_trade_data = "N"
    response_content = None

    try:
        content = response['response']['content']
        if content['size'] != 0 and content['mimeType'] == 'application/json':
            if isinstance(content['text'], str):  # Check for string type
                has_response_trade_data = "Y"
                response_content = content['text']
            else:
                response_content = "N"  # Non-string content
        else:
            response_content = "N"  # Missing or invalid content
    except KeyError:
        response_content = "N"  # Missing 'content' key

    return has_response_trade_data, response_content
#------------------------------------------------------------------------------------------------
def createDataFrame(har):

    FirstParty = ['kotaksecurities']

    ### Extract and clean data
    colmms = [ 'rowid',
            'startedDateTime','url','type','isFetch','host','host-type','method','status','ext','cpcode','ttl','server',
            'cdn-cache','cdn-cache-parent','cdn-cache-key','cdn-req-id','content-length','content-length-origin',
            '_blocked_queueing','blocked','dns','ssl','connect','send','ttfb','receive','time','duration',
            'apiType','isCmotsApi','isEquity','isCommodity','isStockDetailed','isTradingViewData',
            '1newserviceapi','60newserviceapi','decoded_value',
            'cc_code', 'exchange', 'from_date', 'to_date', 'interval', 'asset', 'symbol', 'expiry_date',
            'strike_price', 'strike_price_point', 'option','hasResponseTradeData','responseContent'
    ]
    dat_clean = pd.DataFrame(columns=colmms)


    for i, r in enumerate(har['log']['entries']):
        rowid = (i + 1)  # Adding 1 to start row numbering from 1
        startedDateTime = str(r['startedDateTime'])
        ist_formatted_startedDateTime = str(convertDateTime(startedDateTime))


        u            = str(r['request']['url']).split('?')[0]
        requestType  = str(r['_resourceType'])
        isFetch      = 'Y' if requestType == 'fetch' or requestType =='xhr' else 'N'
        host         = re.search('://(.+?)/', u, re.IGNORECASE).group(0).replace(':','').replace('/','')

        totalTime             = round(r['time'],2) #send,wait,receive,blocked addition
        _blocked_queueing_var = round(r['timings']['_blocked_queueing'],2)
        dnsVar                = round(r['timings']['dns'],2)
        sslVar                = round(r['timings']['ssl'],2)
        connectVar            = round(r['timings']['connect'],2)

        
        if r['request']['method'] == 'GET' and (dnsVar != -1 and sslVar != -1 and connectVar != -1):
            duration = _blocked_queueing_var + totalTime  - r['timings']['receive']
        else:
            duration = _blocked_queueing_var + totalTime - r['timings']['receive'] 

        #analysing the url
        apiType, isCmotsApi, isEquity, isCommodity, isStockDetailed, isTradingViewData ,is1newserviceApi, is60newserviceApi, decoded_value = analyze_url(u)

        #parsed decoded values 
        cc_code, exchange, from_date, to_date, interval, asset, symbol, expiry_date, strike_price, strike_price_point, option = extract_variables(decoded_value)
        
        #check for response trade data
        hasResponseTradeData, responseContent = check_for_response_trade_data(r)

        #cdn-timing
        cachekey = str(findHeader(r,'response','x-cache-key','eq'))
        if not cachekey == 'None':
            cachekey = cachekey.split('/')
            cpcode = int(cachekey[3])
            ttl = cachekey[4]
            cdnCache = str(findHeader(r,'response','x-cache','eq')).split(' ')[0]
            cdnCacheParent = str(findHeader(r,'response','x-cache-remote','eq')).split(' ')[0]
            origin = str(findHeader(r,'response','x-cache-key','eq')).split('/')[5]
        else:
            cachekey = "None"
            cpcode = "None"
            ttl = "None"
            cdnCache = "None"
            cdnCacheParent = "None"
            origin = "None"

        ext = re.search(r'(\.[A-Za-z0-9]+$)', u, re.IGNORECASE)
        if any(tld in host for tld in FirstParty):
            hostType = 'First Party'
        else:
            hostType = 'Third Party'
        
        if ext is None:
            ext = "None"
        else:
            ext = ext.group(0).replace('.','') 
        ct = findHeader(r,'response','content-length','eq')
        if ct == "None":
            ct = 0
        else:
            ct = int(ct)
        if ext in ['jpg','png']:
            ct_origin = findHeader(r,'response','x-im-original-size','eq')
        else:
            ct_origin = findHeader(r,'response','x-akamai-ro-origin-size','eq')
        if ct_origin == "None":
            ct_origin = 0
        else:
            ct_origin = int(ct_origin)
        new_row = {
            'rowid':rowid,
            'startedDateTime':ist_formatted_startedDateTime,
            'url':u,
            'type':requestType,
            'isFetch':isFetch,
            'host':host,
            'host-type':hostType,
            'method':r['request']['method'],
            'status':r['response']['status'],
            'ext':ext,
            'cpcode':cpcode,
            'ttl':ttl,
            'server':str(findHeader(r,'response','server','eq')),
            'cdn-cache':cdnCache,
            'cdn-cache-parent':cdnCacheParent,
            'cdn-cache-key':str(findHeader(r,'response','x-true-cache-key','eq')),
            'cdn-req-id':str(findHeader(r,'response','x-akamai-request-id','eq')),
            'content-length':ct,
            'content-length-origin':ct_origin,
            '_blocked_queueing':str(_blocked_queueing_var),
            'blocked':r['timings']['blocked'],
            'dns': str(dnsVar),
            'ssl': str(sslVar),
            'connect': str(connectVar),
            'send':r['timings']['send'],
            'ttfb':r['timings']['wait'],
            'receive':r['timings']['receive'],
            'time': str(totalTime),
            'duration': str(duration),
            'apiType':apiType,
            'isCmotsApi':isCmotsApi,
            'isEquity':isEquity,
            'isCommodity':isCommodity,
            'isStockDetailed':isStockDetailed,
            'isTradingViewData':isTradingViewData,
            '1newserviceapi':is1newserviceApi,
            '60newserviceapi':is60newserviceApi,
            'decoded_value':decoded_value,
            'cc_code':cc_code,
            'exchange':exchange,
            'from_date':from_date,
            'to_date':to_date,
            'interval':interval,
            'asset':asset,
            'symbol':symbol,
            'expiry_date':expiry_date,
            'strike_price':strike_price,
            'strike_price_point':strike_price_point,
            'option':option,
            'hasResponseTradeData':hasResponseTradeData,
            'responseContent':responseContent

            }

        dat_clean = pd.concat([dat_clean, pd.DataFrame([new_row])],ignore_index=True)

    dat_clean = dat_clean.groupby(colmms).size().reset_index(name='Count')   
    
    # dat_clean.to_csv('Output/harDataset.csv',index=False)   

    #computing flags
    

    return dat_clean




