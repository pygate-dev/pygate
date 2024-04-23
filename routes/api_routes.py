from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from utilities.users import users

api_bp = Blueprint('api_routes', __name__)

@api_bp.route('/api/<apiKey>', methods=['GET'])
@jwt_required()
def createMigrationArtifact(apiKey):
    if not check_api_exists(apiKey):
        return jsonify({'message': 'API does not exist.'}), 400
    users.check_user_role_access_api(get_jwt_identity(), apiKey)

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


@api_bp.route('/api/<apiKey>/subscribe', methods=['POST'])
@jwt_required()
def subscribeToAPI(apiKey):
    if not check_api_exists(apiKey):
        return jsonify({'message': 'API does not exist.'}), 400
    users.check_user_role_access_api(get_jwt_identity(), apiKey)

    if current_user not in user_subscriptions:
        user_subscriptions[current_user] = []

    if apiKey in user_subscriptions[current_user]:
        return jsonify({'message': 'User is already subscribed.'}), 400

    user_subscriptions[current_user].append(apiKey)
    return jsonify({'message': 'User was subscribed.'}), 200

@api_bp.route('/api/<apiKey>/unsubscribe', methods=['POST'])
@jwt_required()
def unsubscribeToAPI(apiKey):
    check_api_exists(apiKey)
    current_user = get_jwt_identity()

    if current_user not in user_subscriptions or apiKey not in user_subscriptions[current_user]:
        return jsonify({'message': 'User is not subscribed.'}), 400

    del user_subscriptions[current_user][user_subscriptions[current_user].index(apiKey)]

    return jsonify({'message': 'User was unsubscribed.'}), 200

@api_bp.route('/backend/<apiKey>/resolve', methods=['POST'])
@jwt_required()
def resolveDownBackend(apiKey):
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_permission_endpoint(current_user)

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

@api_bp.route('/backend/unhealthy', methods=['GET'])
@jwt_required()
def getUnhealthyBackends():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_permission_endpoint(current_user)

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

@api_bp.route('/endpoint', methods=['POST'])
@jwt_required()
def addEndpoint():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_permission_endpoint(current_user)

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

@api_bp.route('/api', methods=['POST'])
@jwt_required()
def addAPI():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_permission_endpoint(current_user)

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

    api_key = Utils.generate_random_key(36)
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
