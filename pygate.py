from flask import Flask, request, jsonify, Response, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

import re, requests, logging, secrets, string, time, uuid

# routes>routing_file
from routes.api_routes import api_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp

# utilties>class_file
from utilities.api import api
from utilities.customJWT import customJWT
from utilities.database import db
from utilities.logger import logger
from utilities.users import users
from utilities.utils import utils

api = api()
customJWT = customJWT()
logger = logger()
users = users()
utils = utils()

pygate = Flask(__name__)

jwt = JWTManager()
jwt.init_app(pygate)
jwt = customJWT.customErrors(jwt)
pygate.config['JWT_SECRET_KEY'] = '345324g5342g5345254534534545t4w3g365uh56886yw567e56u8476867iu76r857r68e5u56u65e6nue5656eu56eu56eu565eu6uu65'
pygate.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=0.5)

pygate.register_blueprint(api_bp)
pygate.register_blueprint(auth_bp)
pygate.register_blueprint(user_bp)

################################### STARTUP ###################################
try:
    db = db()
    print("pygate | Database starting ..")
    db.initializeMongoDB()
    print("pygate | Database startup complete.")
    pygate.run(debug=True)
except Exception as e:
    print("pygate | Startup failed | " + str(e))

################################### GATEWAY ###################################
@pygate.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@jwt_required()
def gateway(path):
    start_time = int(time.time() * 1000)
    request_uuid = str(uuid.uuid4())
    logger.start_log(pygate, request_uuid)

    # Get API/endpoint call information.
    method = request.method
    full_url = request.url
    api_uri = ''
    api_context = ''

    # Get API/endpoint URI information.
    try:
        api_uri = '/api' + full_url.split('/api')[1]
        api_uri_parts = re.split(r'(\/v\d+)', api_uri, maxsplit=1)
        api_context = api_uri_parts[0] + api_uri_parts[1]
        endpoint_uri = api_uri_parts[2]
    except Exception as e:
        logger.end_log(pygate, request_uuid, start_time, "404", int(time.time() * 1000))
        return jsonify({'message': 'Missing API and/or endpoint URI.'}), 404

    # Get the API key.
    if api_context not in api_keys:
        logger.end_log(pygate, request_uuid, start_time, "404", int(time.time() * 1000))
        return jsonify({'message': 'Resource not found.'}), 404
        api_key = api_keys[api_context]

        current_user = get_jwt_identity()

        user_role = users_roles[current_user]
    if user_role not in api_user_roles[api_key]:
        return jsonify({'message': 'User does not have sufficient role access.'}), 401

    if user_role != 'admin' and api_key not in user_subscriptions[current_user]:
        return jsonify({'message': 'User is not subscribed to this API.'}), 401

    # Remove query params from endpoint uri.
    if '?' in endpoint_uri:
        endpoint_uri = endpoint_uri.split('?')[0]

    # Check if endpoint exists.
    if api_key not in api_endpoints or method+endpoint_uri not in api_endpoints[api_key]:
        logger.end_log(pygate, request_uuid, start_time, "404", int(time.time() * 1000))
        return jsonify({'message': 'Endpoint not found.'}), 404

    # Get the API backend information.
    if api_key not in api_backends:
        logger.end_log(pygate, request_uuid, start_time, "500", int(time.time() * 1000))
        return jsonify({'message': 'No backend configured.'}), 500

    # Get endpoint info:
    def get_api_endpoint(method, api_context, endpoint_uri):
        endpoint = api_backend_api_endpoint[method + api_context + endpoint_uri]
        return endpoint

    # Get the backend url for the API.
    def get_api_backend(api_key, api_backend_index, retry):
        backend = api_backends[api_key][api_backend_index]
        if retry:
            pygate.logger.info(request_uuid + " | Retry backend: " + backend)
        else:
            pygate.logger.info(request_uuid + " | Backend: " + backend)
        return backend

    # Get next API node backend for load balancing.
    def get_backend_rotation(api_key):
        if api_backend_rotation[api_key] >= len(api_backends[api_key]):
            api_backend_rotation[api_key] = 0
        api_backend_index = api_backend_rotation[api_key]
        api_backend_rotation[api_key] += 1
        return api_backend_index

    def calc_kb(request):
        if request:
            content_length = request.content_length
            headers_size = len(request.headers)  # Approximate size based on headers count
            query_string_size = len(request.query_string) if request.method == 'GET' else 0
            if not content_length: content_length = 0
            if not headers_size: headers_size = 0
            if not query_string_size: query_string_size = 0
            total_size_bytes = content_length + headers_size + query_string_size
            return total_size_bytes / 1024

    # Call to external resource.
    def external_call(request, method, api_context, api_key, api_backend_index, backend, backend_endpoint, attempts):
        try:
            response = None
            if method == "GET":
                if request.data:
                    response = requests.get(backend + backend_endpoint, json=request.data)
                else:
                    response = requests.get(backend + backend_endpoint)
                return jsonify(response.json()), response.status_code
            elif method == "POST":
                if request.data:
                    response = requests.post(backend + backend_endpoint, json=request.data)
                else:
                    response = requests.post(backend + backend_endpoint)
                return jsonify(response.json()), response.status_code
            elif method == "PUT":
                if request.data:
                    response = requests.put(backend + backend_endpoint, json=request.data)
                else:
                    return [jsonify(response.json()), response.status_code]
                return jsonify(response.json()), response.status_code
            elif method == "DELETE":
                if request.data:
                    response = requests.delete(backend + backend_endpoint, json=request.data)
                else:
                    response = requests.delete(backend + backend_endpoint)
                return jsonify(response.json()), response.status_code
        except Exception as e:
            # Remove the down node.
            if api_key not in unhealthy_urls:
                unhealthy_urls[api_key] = []
                unhealthy_apis[api_key] = api_context
            unhealthy_urls[api_key].append(api_backends[api_key][api_backend_index])
            del api_backends[api_key][api_backend_index]

            # Try until no backends are available.
            if len(api_backends[api_key]) != 0:
                backend = get_api_backend(api_key, api_backend_index, True)
                external_call(request, method, api_context, api_key, api_backend_index, backend, backend_endpoint, attempts + 1)

            return jsonify({'message': 'Internal server error.'}), 500

        api_backend_index = get_backend_rotation(api_key)
        backend = get_api_backend(api_key, api_backend_index, False)
        backend_endpoint = get_api_endpoint(method, api_context, endpoint_uri)
        pygate.logger.info(request_uuid + " | Endpoint: " + request.path)
        before_out_time = int(time.time() * 1000)

        # Temp code for calculating total kb
        if "0" not in total_data_out:
            total_data_out["0"] = 0
        total_data_out["0"] += calc_kb(request)

        response, status_code = external_call(request, method, api_context, api_key, api_backend_index, backend, backend_endpoint, 0)
        logger.end_log(pygate, request_uuid, start_time, str(status_code), before_out_time)
        return response
