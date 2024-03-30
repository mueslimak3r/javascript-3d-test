import requests
import json
from time import sleep
from requests.exceptions import SSLError, ConnectionError
from os import environ as env

API_URL = 'http://appserver-docker1.home.arpa:4000/api/' if not 'API_URL' in env else env['API_URL']

api = {
    "wars": {
        "url": [],
        "headers": {},
        "params": {}
	},
    "war_planets": {
        "url": [
            "warId",
            "planets"
        ],
        "headers": {},
        "params": {}
	},
}

def request_with_retry(session, url, params={}):
    for _ in range(10):
        try:
            response = session.get(url, params=params)
            return response
        except (ConnectionError, SSLError) as e:
            print(e)
            print('retrying')
            pass
        sleep(0.5)
    return None

def api_call_internal(query):
    url = API_URL + "/".join(query['url'])
    print(url)
    query['headers']['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
    session = requests.session()
    session.headers.update(query['headers'])

    response = request_with_retry(session, url, query['params'])
    if response is None:
        return {}
    if response.status_code != 200:
        print(response.status_code)
        return {}
    # print(response.text)
    result = json.loads(response.text)
    return result

def api_call(query):
    response = api_call_internal(query)
    if response is None:
        return {}
    return response if type(response) is dict else { "content": response }

def get_wars():
    print('getting wars')
    query = api["wars"]
    
    wars = api_call(query)
    return wars

def get_war_planets(war_id):
    print('getting war planets')
    query = api["war_planets"]
    query['url'][0] = str(war_id)    
    events = api_call(query)
    return events['content']

if __name__ == "__main__":
    wars = get_wars()
    print(json.dumps(wars, indent=4))
    current_war = wars['current']
    result = get_war_planets(current_war)
    print(json.dumps(result, indent=4))
