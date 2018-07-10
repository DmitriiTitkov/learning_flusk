from flask import Blueprint, request
from flask_restful import Resource, Api
from flasgger import swag_from
from typing import Dict, Any


cookie_bp: Blueprint = Blueprint('cookie_bp', __name__, template_folder='templates')
api = Api(cookie_bp)


# Cookies
class Cookies(Resource):
    @swag_from('open_api_specs/cookies_get.yml', validation=False)
    def get(self):
        return request.cookies, 200

    @swag_from('open_api_specs/cookies_post.yml', validation=True)
    def post(self):
        return request.json, 201, {'Set-Cookie': '{}={}'.format(request.json['name'], request.json['value'])}


class Cookie(Resource):
    @swag_from('open_api_specs/cookie_get.yml', validation=False)
    def get(self, cookie_name: str):  # TODO finish methods get and put
        if not request.cookies.get(cookie_name, None):
            return {'error': "Couldn't find cookie: {}".format(cookie_name)}, 404

        return {cookie_name: request.cookies[cookie_name]}, 200

    @swag_from('open_api_specs/cookie_put.yml', validation=False)
    def put(self, cookie_name: str):
        response: int = request.cookies.get(cookie_name, None) and 200 or 201
        cookie: str = '{}={}'.format(request.json['name'], request.json['value'])
        return cookie, response, {'Set-Cookie': cookie}

    @swag_from('open_api_specs/cookie_delete.yml', validation=False)
    def delete(self, cookie_name: str):
        if not request.cookies.get(cookie_name, None):
            return {'error': "Couldn't find cookie: {}".format(cookie_name)}, 404
        cookie: str = '{}={}; Expires={}'.format(cookie_name, '', 0)
        return "", 200, {'Set-Cookie': cookie}


api.add_resource(Cookies, '/cookies')
api.add_resource(Cookie, '/cookies/<string:cookie_name>')