import requests
from flask import Flask,request,jsonify
from flask_caching import Cache




app = Flask(__name__)


app.config['CACHE_TYPE'] = 'SimpleCache'  # Можно выбрать другой тип кэша, например, Redis
cache = Cache(app)

def get_operator_name(number):
    print('get operator name ', number)
    base_url = "https://num.voxlink.ru/get/"
    # Параметры запроса
    params = {
        "num": number,
    }

    # Выполнение GET-запроса с параметрами
    response = requests.get(base_url, params=params)
    if response.status_code == 404:
        return {'operator': '404'}
    if response.status_code != 200:
        return None
    return response.json()


def cached_call(number=None):
    cached = cache.get(number)

    if cached is None:
        json_from_voxlink = get_operator_name(number)
        if json_from_voxlink != None:
            cache.set(number, json_from_voxlink)
        return json_from_voxlink
    return cached


@app.route('/voxlink')
def voxlink_json():
    number = request.args.get('num', None)
    return cached_call(number)

@app.route('/voxlink/operator')
def voxlink_operator():
    number = request.args.get('num', None)
    json_from_voxlink = cached_call(number)
    if json_from_voxlink is not None:
        operator_name = json_from_voxlink.get('operator')
        return operator_name
    return ''

if __name__ == "__main__":
    number = 79625864175
    result = get_operator_name(number)
    print(result)