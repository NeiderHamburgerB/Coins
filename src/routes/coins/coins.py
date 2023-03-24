import os
import json
from requests import get
from src.config.database.provider import connection

def values(connection):
    btc_query = "SELECT price_usd,created_at FROM btc_prices ORDER BY created_at DESC"
    eth_query = "SELECT price_usd,created_at FROM eth_prices ORDER BY created_at DESC"
    
    cursor = connection.cursor()

    #btc
    cursor.execute(btc_query)
    btc_results = cursor.fetchall()
    btc_prices = [row[0] for row in btc_results]
    btc_dates = [row[1] for row in btc_results]

    #eth
    cursor.execute(eth_query)
    eth_results = cursor.fetchall()
    eth_prices = [row[0] for row in eth_results]
    eth_dates = [row[1] for row in eth_results]
    
    result = {
        "eth": {
            "prices": eth_prices,
            "dates": eth_dates
        },
        "btc": {
            "prices": btc_prices,
            "dates": btc_dates
        }
    }
    
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(result, indent=4, sort_keys=True, default=str)
    }

    return response

def getData(event, context):
    connect = connection()
    result = values(connect)
    return result
    
def getInfoGeneral(event, context):
    try:
        headers = {'X-CMC_PRO_API_KEY': os.environ['API_KEY']}
        response = get(os.environ['URI_GLOBAL'], headers=headers)
        data = response.json()

        cryptos = data['data']['active_cryptocurrencies']
        exchanges = data['data']['active_exchanges']
        market_cap = '${:,.0f}'.format(data['data']['quote']['USD']['total_market_cap'])
        vol_24h = '${:,.0f}'.format(data['data']['quote']['USD']['total_volume_24h'])
        
        response = {'statusCode': 200,'body': json.dumps({
            'cryptos': cryptos,
            'exchanges': exchanges,
            'market_cap': market_cap,
            'vol_24h': vol_24h
        }) }
        
        response['headers'] = {'Access-Control-Allow-Origin': '*'}

        return response

    except Exception as e:
        body = {'message': 'Sorry an error occurred', 'error': str(e)}
        response = {'statusCode': 500, 'body': json.dumps(body)}
        response['headers'] = {'Access-Control-Allow-Origin': '*'}
        
    return response
   

def save(data,connection):

    try:
        btc_query = "INSERT INTO btc_prices (price_usd, created_at) VALUES (%s, NOW())"
        eth_query = "INSERT INTO eth_prices (price_usd, created_at) VALUES (%s, NOW())"
        
        btc_value = (data['BTC']['price_usd'],)
        eth_value = (data['ETH']['price_usd'],)
    
        cursor = connection.cursor()
        cursor.execute(btc_query, btc_value)
        cursor.execute(eth_query, eth_value)
        connection.commit()
        cursor.close()
    except Exception as e:
        body = {'message': 'Sorry an error occurred', 'error': str(e)}
        response = {'statusCode': 500, 'body': json.dumps(body)}
        response['headers'] = {'Access-Control-Allow-Origin': '*'}
        
   
def getPrices(event, context):
    try:
        headers = {'X-CMC_PRO_API_KEY': os.environ['API_KEY']}
        coins = ['BTC', 'ETH'] 
        result = {} 

        for coin in coins:
            response = get(os.environ['URI_BASE'] + coin, headers=headers)
            data = response.json()['data'][coin]
            price_usd = data['quote']['USD']['price']
            result[coin] = {
                'price_usd': round(price_usd,2)
            }

        connect = connection()
        save(result,connect)
        body = {'data': result}
        response = {'statusCode': 200, 'body': json.dumps(body)}
        response['headers'] = {'Access-Control-Allow-Origin': '*'}
        
        
    except Exception as e:
        body = {'message': 'Sorry an error occurred', 'error': str(e)}
        response = {'statusCode': 500, 'body': json.dumps(body)}
        response['headers'] = {'Access-Control-Allow-Origin': '*'}
        

    return response

