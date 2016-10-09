import requests, json
from templates.button import *
from pprint import pprint
from geopy.geocoders import Nominatim

headers = {'Accept': 'application/json', 'user_key': 'ada7140b071d43fe7ac36c260b854174', 'User-Agent': 'curl/7.35.0'}


def get_location(location):
    key = "AhuYVYvwc666R0W_9dNUo9sTq1YjyzIzU4QdRD_7wB1qdb75BwoZj4Rg7tgpyLM9"
    url = "http://dev.virtualearth.net/REST/v1/Locations/" + location + "?inclnb=1&o=json&key=" + key
    request = requests.get(url)
    # pprint(request.text)
    response = json.loads(request.text)
    result = response['resourceSets'][0]['resources'][0]['point']['coordinates']
    return result[0], result[1]


def get_template(restaurants):
    generic_template = {
        "attachment": {
        "type": "template",
        "payload": {
            'template_type': 'generic',
            'value': {
                'attachment': {
                    'type': 'template',
                    'payload': {
                        'template_type': 'generic',
                        'elements': []
                    }
                }
            }
        }
    }}
    for restaurant in restaurants:
        element = {'title': restaurant['name'], 'item_url': restaurant['url'], 'image_url': restaurant['image_url'],
                   'buttons': [
                       {
                           "type": "web_url",
                           "url": restaurant['url'],
                           "title": "Visit Website"
                       },
                       {
                           "type": "postback",
                           "title": "Get Reviews",
                           "payload": "get_reviews"
                       },
                       {
                           "type": "postback",
                           "title": "Get Directions",
                           "payload": "get_directions"
                       },
                   ]}
        generic_template['value']['attachment']['payload']['elements'].append(element)
    return generic_template


def process(action, parameters):
    output = {}
    if parameters['geo-city'] is None or parameters['number-integer'] is None:
        return output
    lat, lon = get_location(parameters['geo-city'])
    url = 'https://developers.zomato.com/api/v2.1/search?count=10' + '&lat=' + str(
        lat) + '&lon=' + str(lon)
    if parameters['cuisines'] is not None:
        url += "&cuisines=" + parameters['cuisines']
    try:
        r = requests.get(url, headers=headers)
        restaurants = []
        if r.status_code != 200:
            print "Api Issues"
            return
        if len(r.json()['restaurants']) <= 0:
            print "Api Issues"
            return
        for res in r.json()['restaurants']:
            rest = {}
            rest['budget'] = res['restaurant']['currency'] + ' ' + str(
                float(res['restaurant']['average_cost_for_two']) / 2)
            # if rest['budget'] > parameters['number-integer']:
            #     continue
            rest['id'] = res['restaurant']['id']
            rest['name'] = res['restaurant']['name']
            rest['url'] = res['restaurant']['url']
            rest['location_lat'] = res['restaurant']['location']['latitude']
            rest['location_lon'] = res['restaurant']['location']['longitude']
            rest['rating'] = res['restaurant']['user_rating']['aggregate_rating']
            rest['locality'] = res['restaurant']['location']['locality']
            rest['image_url'] = res['restaurant']['thumb']
            restaurants.append(rest)
        # pprint(restaurants)
        template1 = get_template(restaurants)
        output['action'] = action
        output['output'] = template1
        output['success'] = True
    except:
        print "Network Error!"
        error_message = 'I couldn\'t find any Restaurant matching your query.'
        error_message += '\nPlease ask me something else, like:'
        error_message += '\n  - Some restaurants in guwahati under 1000 Rs'
        error_message += '\n  - Any place to eat in Mumbai'
        error_message += '\n  - I\'m Hungry'
        output['error_msg'] = TextTemplate(error_message).get_message()
        output['success'] = False
    return output


if __name__ == '__main__':
    pass
