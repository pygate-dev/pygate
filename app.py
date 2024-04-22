from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from pymongo import MongoClient

import re, requests, logging, secrets, string, time, uuid, platform, subprocess

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '345324g5342g5345254534534545t4w3g365uh56886yw567e56u8476867iu76r857r68e5u56u65e6nue5656eu56eu56eu565eu6uu65'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=0.5)
jwt = JWTManager(app)
db = None

def getMongoDB():
    client = MongoClient('localhost', 27017)
    # Connect to the 'mydatabase' database
    db = client['pygate']

def createMongoDB():
    # Connect to MongoDB (assuming it's running locally on default port)
    client = MongoClient('localhost', 27017)

    # Create to the 'mydatabase' database
    db = client['pygate']

    # Check if collection already exists.
    collection_list = db.list_collection_names()
    if "user_credentials" in collection_list:
        app.logger.info("pygate | Database already initialized.")
        return

    collections = ['user_credentials', 'user_roles', 'users_roles', 'user_subscriptions',
                   'api_keys', 'api_contexts', 'api_backends', 'api_backend_rotation',
                   'api_endpoints', 'api_backend_api_endpoint', 'api_user_roles',
                   'unhealthy_apis', 'unhealthy_urls']

    for collection_name in collections:
            db.create_collection(collection_name)

    # Define indexes.
    user_credentials_collection.create_index([('username', 1)], unique=True)
    user_roles_collection.create_index([('role', 1)], unique=True)
    users_roles_collection.create_index([('username', 1)], unique=True)
    user_subscriptions_collection.create_index([('username', 1)], unique=True)
    api_keys_collection.create_index([('api_context', 1)], unique=True)
    api_contexts_collection.create_index([('apiKey', 1)], unique=True)
    api_backends_collection.create_index([('apiKey', 1)], unique=True)
    api_backend_rotation_collection.create_index([('api_key', 1)], unique=True)
    api_endpoints_collection.create_index([('api_key', 1)], unique=True)
    api_backend_api_endpoint_collection.create_index([('api_key', 1)], unique=True)
    api_user_roles_collection.create_index([('apiKey', 1)], unique=True)
    unhealthy_apis_collection.create_index([('apiKey', 1)], unique=True)
    unhealthy_urls_collection.create_index([('apiKey', 1)], unique=True)

    app.logger.info("pygate | Database initialization successful.")

def startMongoDB():
    subprocess_args = ["./mongodb/windows/bin/mongod", "--dbpath", "./mongodb/data"]
    if platform.system() == "Windows":
        subprocess_args[0] += ".exe"
    subprocess.run(subprocess_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def mongoDBCheck():
    return

def initializeMongoDB():
    app.logger.info("pygate | Starting .."
    # MongoDB startup/initialization
    createMongoDB()
    app.logger.info("pygate | Startup complete."

total_data_out = {}

# These dicts are examples and will be replaced by a db.
user_credentials = {
'mitch': 'password'
}
user_roles = {
'admin':'',
'standard':''
}
users_roles = {
'mitch': 'admin'
}
user_subscriptions = {
'mitch' : []
}

api_keys = {}
api_contexts = {}
api_backends  = {}
api_backend_rotation = {}
api_endpoints = {}
api_backend_api_endpoint = {}
api_user_roles = {}

unhealthy_apis = {}
unhealthy_urls = {}

# Custom error handler for JWT errors.
@jwt.expired_token_loader
def expired_token_callback(one, two):
    return jsonify({'message': 'Token has expired.'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token.'}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({'message': 'Unauthorized access.'}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({'message': 'Fresh token required.'}), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({'message': 'Token has been revoked.'}), 401

def generate_random_key(length):
    alphabet = string.ascii_letters + string.digits
    key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return key

def check_user_role_access_api(current_user, apiKey):
    user_role = ''
    if current_user in users_roles:
        user_role = users_roles[current_user]
    if user_role not in api_user_roles[apiKey]:
        return jsonify({'message': 'User role does not have access to this API.'}), 403

def check_permission_endpoint(current_user):
    user_role = ''
    if current_user in users_roles:
        user_role = users_roles[current_user]
    if user_role != 'admin':
        return jsonify({'message': 'You do not have permission to access this endpoint.'}), 403

def check_api_exists(apiKey):
    return apiKey in api_contexts

def start_log(request_uuid):
    app.logger.info(request_uuid + " | ----- Start request ----- ")

def end_log(request_uuid, start_time, status = "", before_out_time = 0):
    current_time = int(time.time() * 1000)
    if len(status) > 0:
        app.logger.info(request_uuid + " | Status: " + status)
    if before_out_time:
        app.logger.info(request_uuid + " | Time in gateway: " + str(before_out_time - start_time) + "ms")
        app.logger.info(request_uuid + " | API Backend time: " + str(current_time - before_out_time) + "ms")
    app.logger.info(request_uuid + " | Total response time: " + str(current_time - start_time) + "ms")
    app.logger.info(request_uuid + " | ----- End request ----- ")

def ping_server(hostname, port=80):
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)  # Set a timeout of 1 second
        # Connect to the server
        s.connect((hostname, port))
        s.close()
        return True
    except:
        return False

@app.route('/api/<apiKey>', methods=['GET'])
@jwt_required()
def createMigrationArtifact(apiKey):
    if not check_api_exists(apiKey):
        return jsonify({'message': 'API does not exist.'}), 400
    check_user_role_access_api(get_jwt_identity(), apiKey)

    current_api_key = apiKey
    current_api_context = api_contexts[current_api_key]
    current_api_backends  = api_backends[current_api_key]
    current_api_endpoints = api_endpoints[current_api_key]
    current_api_backend_api_endpoints = {}
    for endpoint in current_api_endpoints:
        current_endpoint_method = endpoint.split('/')[0]
        current_endpoint_uri = method = endpoint.split('/')[1]
        current_api_backend_api_endpoints[current_endpoint_method + current_api_context + '/' + current_endpoint_uri] = api_backend_api_endpoint[current_endpoint_method + current_api_context  + '/' + current_endpoint_uri]
    current_api_user_roles = api_user_roles[current_api_key]

    return jsonify({
        'apiKey' : current_api_key, 'apiContext' : current_api_context, 'apiBackends' : current_api_backends, 'apiEndpoints' : current_api_endpoints, 'apiBackendEndpoints' : current_api_backend_api_endpoints, 'apiUserRoles' : current_api_user_roles
    }), 200


@app.route('/api/<apiKey>/subscribe', methods=['POST'])
@jwt_required()
def subscribeToAPI(apiKey):
    if not check_api_exists(apiKey):
        return jsonify({'message': 'API does not exist.'}), 400
    check_user_role_access_api(get_jwt_identity(), apiKey)

    if current_user not in user_subscriptions:
        user_subscriptions[current_user] = []

    if apiKey in user_subscriptions[current_user]:
        return jsonify({'message': 'User is already subscribed.'}), 400

    user_subscriptions[current_user].append(apiKey)
    return jsonify({'message': 'User was subscribed.'}), 200

@app.route('/api/<apiKey>/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribeToAPI(apiKey):
    check_api_exists(apiKey)
    current_user = get_jwt_identity()

    if current_user not in user_subscriptions or apiKey not in user_subscriptions[current_user]:
        return jsonify({'message': 'User is not subscribed.'}), 400

    del user_subscriptions[current_user][user_subscriptions[current_user].index(apiKey)]

    return jsonify({'message': 'User was unsubscribed.'}), 200

@app.route('/backend/<apiKey>/resolve', methods=['POST'])
@jwt_required()
def resolveDownBackend(apiKey):
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    if apiKey in unhealthy_apis and unhealthy_urls[apiKey]:
        for i, node in enumerate(unhealthy_apis[apiKey]):
            if ping_server(node):
                del unhealthy_urls[key][i]
                api_backends[key].append(node)
        if apiKey in unhealthy_apis and not unhealthy_apis[apiKey]:
            del unhealthy_apis[apiKey]
            del unhealthy_urls[apiKey]
        return jsonify({'message': 'Any live nodes were resolved.'}), 200
    else:
        return jsonify({'message': 'This resource has no down nodes.'}), 400

@app.route('/backend/unhealthy', methods=['GET'])
@jwt_required()
def getUnhealthyBackends():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    if unhealthy_urls:
        data = []
        for key, api in unhealthy_apis.items():
            data.append({
                      "apiName": api,
                      "apiKey": key,
                      "downBackends": unhealthy_urls[key]
                    })
        return jsonify(data), 200
    else:
        return jsonify({}), 204

@app.route('/endpoint', methods=['POST'])
@jwt_required()
def addEndpoint():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    # Get json data from the request body.
    request_body = request.json
    api_name = '/' + request_body.get('apiName')
    api_version = '/' + request_body.get('apiVersion')
    endpoint_uri = request_body.get('endpointURI')
    backend_endpoint_uri = request_body.get('backendEndpointURI')
    method = request_body.get('method')

    # Ensure all data is passed into the request body.
    # TODO: Individual field payload validation.
    if not api_name or not api_version or not endpoint_uri or not backend_endpoint_uri or not method:
        return jsonify({'message': 'Missing required field.'}), 400

    # Check if the API exists.
    api_context = ('/api' + api_name + api_version).lower()
    if api_context not in api_keys:
        return jsonify({'message': 'API does not exist.'}), 400
    api_key = api_keys[api_context]

    # Add the endpoint to the endpoint list.
    if api_key not in api_endpoints:
        api_endpoints[api_key] = []
    if method+endpoint_uri in api_endpoints[api_key]:
        return jsonify({'message': 'Endpoint already exists.'}), 400
    api_endpoints[api_key].append(method+endpoint_uri)
    api_backend_api_endpoint[method+api_context+endpoint_uri] = backend_endpoint_uri

    return jsonify({'message': 'Endpoint Created.'}), 201

@app.route('/api', methods=['POST'])
@jwt_required()
def addAPI():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    # Ensure all data is passed into the request body.
    # TODO: Individual field payload validation.
    request_body = request.json
    if not request_body.get('apiName') or not request_body.get('apiVersion') or not request_body.get('backends'):
        return jsonify({'message': 'Missing required field.'}), 400

    api_context = '/api/' + request_body.get('apiName').lower() + '/' + request_body.get('apiVersion').lower()
    if api_context in api_keys:
        return jsonify({'message': 'API already exists.'}), 400

    api_roles = ["admin"]
    if request_body.get('userRoles'):
        api_roles +=  request_body.get('userRoles')

    api_key = generate_random_key(36)
    api_keys[api_context] = api_key
    api_contexts[api_key] = api_context

    api_user_roles[api_key] = api_roles

    if api_key not in api_backends:
        api_backends[api_key] = []
        api_backend_rotation[api_key] = -1

    for backend in request_body.get('backends'):
        api_backends[api_key].append(backend.lower())
        api_backend_rotation[api_key] += 1

    api_backend_rotation[api_key] = 0

    return jsonify({'message': 'API Created.'}), 201

@app.route('/user/<userId>', methods=['DELETE'])
@jwt_required()
def removeUser(userId):
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    # A user cannot delete themself.
    if current_user == userId:
        return jsonify({'message': 'Unable to remove self.'}), 400

    # Delete the user if they exist.
    if userId and userId in user_credentials:
            del user_credentials[userId]
            del users_roles[userId]
    else:
        return jsonify({'message': 'User does not exists.'}), 400

    return jsonify({'message': 'User removed.'}), 200

@app.route('/user', methods=['POST'])
@jwt_required()
def addUser():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    check_permission_endpoint(current_user)

    # Get json data from the request body.
    request_body = request.json
    username = request_body.get('username')
    password = request_body.get('password')
    role = request_body.get('role')

    # Ensure the username doesn't already exist and the role is valid.
    if username and username not in user_credentials:
        if role and role in user_roles:
            user_credentials[username] = password
            users_roles[username] = role
            user_subscriptions[username] = []
        else:
            return jsonify({'message': 'Role does not exist.'}), 400
    else:
        return jsonify({'message': 'User already exists.'}), 400

    return jsonify({'message': 'User created.'}), 201


@app.route('/authorization', methods=['POST'])
def authorization():
    # Get json data from the request body.
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Ensure all data is passed into the request.
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Check if user exists and the password is valid.
    if username not in user_credentials or user_credentials[username] != password:
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate access token.
    access_token = create_access_token(identity=username)
    return jsonify(authorizationToken=access_token), 200

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@jwt_required()
def gateway(path):
    start_time = int(time.time() * 1000)
    request_uuid = str(uuid.uuid4())
    start_log(request_uuid)

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
        end_log(request_uuid, start_time, "404", int(time.time() * 1000))
        return jsonify({'message': 'Missing API and/or endpoint URI.'}), 404

    # Get the API key.
    if api_context not in api_keys:
        end_log(request_uuid, start_time, "404", int(time.time() * 1000))
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
        end_log(request_uuid, start_time, "404", int(time.time() * 1000))
        return jsonify({'message': 'Endpoint not found.'}), 404

    # Get the API backend information.
    if api_key not in api_backends:
        end_log(request_uuid, start_time, "500", int(time.time() * 1000))
        return jsonify({'message': 'No backend configured.'}), 500

    # Get endpoint info:
    def get_api_endpoint(method, api_context, endpoint_uri):
        endpoint = api_backend_api_endpoint[method + api_context + endpoint_uri]
        return endpoint

    # Get the backend url for the API.
    def get_api_backend(api_key, api_backend_index, retry):
        backend = api_backends[api_key][api_backend_index]
        if retry:
            app.logger.info(request_uuid + " | Retry backend: " + backend)
        else:
            app.logger.info(request_uuid + " | Backend: " + backend)
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
    app.logger.info(request_uuid + " | Endpoint: " + request.path)
    before_out_time = int(time.time() * 1000)

    # Temp code for calculating total kb
    if "0" not in total_data_out:
        total_data_out["0"] = 0
    total_data_out["0"] += calc_kb(request)

    response, status_code = external_call(request, method, api_context, api_key, api_backend_index, backend, backend_endpoint, 0)
    end_log(request_uuid, start_time, str(status_code), before_out_time)
    return response

if __name__ == '__main__':
    try:
        startMongoDB()
        initializeMongoDB()
        app.run(debug=True)
    except Exception as e:
        app.logger.info("pygate | Startup failed | " + String(e))
