from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token

from utilities.users import Users
from utilities.database import DB

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/authorization', methods=['POST'])
def authorization():
    # Get json data from the request body.
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Ensure all data is passed into the request.
    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    # Check if user exists and the password is valid.
    db = DB()
    user_credentials = db.singleQuery("user_credentials", "username", username)
    print(user_credentials)
    if not user_credentials or user_credentials["username"] != username or user_credentials["password"] != password:
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate access token.
    access_token = create_access_token(identity=username)
    return jsonify(authorizationToken=access_token), 200

@auth_bp.route('/authorization/jwt-settings', methods=['PUT'])
@jwt_required()
def jwt_settings():
    current_user = get_jwt_identity()
    users.check_admin_endpoint(current_user)

    # Get json data from the request body.
    data = request.json
    jwtExpire = data.get('jwtExpire')

    # Ensure all data is passed into the request.
    if not jwtExpire:
        return jsonify({'message': 'Missing jwtExpire field'}), 400

    from pygate import pygate

    pygate.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=jwtExpire)

    # Generate access token.
    access_token = create_access_token(identity=username)
    return jsonify(authorizationToken=access_token), 200
