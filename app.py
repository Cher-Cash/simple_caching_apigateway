import requests
from flask import Flask, request, jsonify
from flask_caching import Cache
from time import sleep

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


def cached_call(number=None, retry=3, timeout=2):
    cached = cache.get(number)
    if cached is not None:
        return cached

    for i in range(0, retry):
        json_from_voxlink = get_operator_name(number)
        if json_from_voxlink is not None:
            cache.set(number, json_from_voxlink)
            cached = json_from_voxlink
        else:
            sleep(timeout)
    return cached


@app.route('/voxlink')
def voxlink_json():
    number = request.args.get('num', None)
    retry = app.config.get('retry', 3)
    timeout = app.config.get('timeout', 2)
    return jsonify(cached_call(number, retry=retry, timeout=timeout))


@app.route('/voxlink/operator')
def voxlink_operator():
    number = request.args.get('num', None)
    retry = app.config.get('retry', 3)
    timeout = app.config.get('timeout', 2)
    json_from_voxlink = cached_call(number, retry=retry, timeout=timeout)
    if json_from_voxlink is not None:
        operator_name = json_from_voxlink.get('operator')
        return operator_name
    return ''


if __name__ == "__main__":
    number = 79625864175
    result = get_operator_name(number)
    print(result)
