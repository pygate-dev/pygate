from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

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
    if username not in user_credentials or user_credentials[username] != password:
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate access token.
    access_token = create_access_token(identity=username)
    return jsonify(authorizationToken=access_token), 200
