from flask import Flask, Request, jsonify, request, make_response, render_template
from flasgger import Swagger
from flask_restful import Api
import random
from blueprints.cookies import cookie_bp

from constants import http_codes
from flask.wrappers import Response
from typing import Union, Optional

app: Flask = Flask(__name__)
api = Api(app)
swagger = Swagger(app)
request: Request = request


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


# Request inspection
@app.route('/headers', methods=['GET'])
def headers():
    """
    Returns list of all headers
    ---
    tags:
      - "Request inspection"
    parameters: []
    responses:
       200:
        description: "All list of headers"
        content:
            application/json:
              schema:
              type: object
              additionalProperties:
                type: string
    """
    return jsonify(dict(request.headers.to_list("UTF8")))


@app.route('/ip', methods=['GET'])
def ip():
    """
    Returns requester's ip address
    ---
    tags:
      - "Request inspection"
    parameters: []
    responses:
       200:
        description: "requester's ip address"
        content:
            application/json:
              schema:
              type: object
              additionalProperties:
                type: string
    """
    return jsonify({'ip_address': request.remote_addr})


@app.route('/user_agent', methods=['GET'])
def user_agent():
    """
    Returns requester's user agent
    ---
    tags:
      - "Request inspection"
    parameters: []
    responses:
       200:
        description: "requester's user agent"
        content:
            application/json:
              schema:
              type: object
              additionalProperties:
                type: string
    """
    return jsonify({'user_agent': request.user_agent.string})


# Statuses
@app.route("/status/<codes>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "TRACE"])
def status(codes: str):
        """
        Returns status code passed as url path or a random if many were passed.
        ---
        tags:
            - Status Codes
        produces:
            - text/html
        parameters:
                - in: path
                  name: codes
                  type: string
                  required: true
        responses:
          100:
            description: Informational responses
          200:
            description: Success
          300:
            description: Redirection
          400:
            description: Client Errors
          500:
            description: Server Errors
        """
        random_code_str: str = random.choice(codes.split(","))
        try:
            random_code: int = int(random_code_str)
            if random_code not in http_codes:
                return {'error': "Unknown Http code: {}".format(random_code_str)}, 400

        except ValueError:
            return {'error': "Unknown Http code: {}".format(random_code_str)}, 400

        return '', random_code


# Response inspection   # TODO Check headers, especially content-type
@app.route("/response_headers", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "TRACE"])
def response_headers():
    """
    Response headers
    ---
    tags:
      - "Response inspection"
    parameters: []
    responses:
       200:
        description: "successful operation"
    """
    response: Response = make_response('')
    return jsonify(dict(response.headers))


@app.route("/cache", methods=["GET"])
def cache():  # TODO review and finish
    """
    Returns a 304 if an If-Modified-Since header or If-None-Match is present. Returns the same as a GET otherwise.
    ---
    tags:
      - "Response inspection"
    parameters:
        - name: If-Modified-Since
          in: header
        - name: If-None-Match
          in: header
    responses:
       200:
        description: Cached response
       304:
        description: Modified

    """
    header_persist = request.headers.get('If-Modified-Since') or request.headers.get('If-None-Match')

    if header_persist:
        return '', 304

    return request.json, 200


@app.route("/etag/<string:etag>", methods=["GET"])  # TODO validate and re - check
def e_tag(etag):
    """
    Assumes the resource has the given etag and responds to If-None-Match and If-Match headers appropriately.
    ---
    tags:
      - "Response inspection"
    parameters:
        - name: etag
          in: path
        - name: If-Match
          in: header
        - name: If-None-Match
          in: header
    responses:
       200:
        description: Normal response
       304:
        description: cached
       412:
        description: match
    """
    if_none_match = request.headers.get("If-None-Match")
    if_match = request.headers.get("If-Match")

    if if_none_match == etag:
        return '', 304

    if if_match != etag:
        return '', 412

    return request.json, 200


# Anything

@app.route('/anything/', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "TRACE"])
@app.route('/anything/<path:anything>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "TRACE"])
def anything(anything: Optional[str] = None):
        """
        Returns any data passed
        ---
        tags:
          - "Anything"
        produces:
            - application/json
        responses:
          200:
            description: "Returns passed data"

        """

        return jsonify({"args": request.args, "files": request.files, "form": request.form,
                        "headers": dict(request.headers.to_list("UTF8")), "json": request.json,
                        "method": request.method, "origin": request.remote_addr, "url": request.url})


ar = api.add_resource
app.register_blueprint(cookie_bp)


if __name__ == "__main__":
    app.run(debug=True)
