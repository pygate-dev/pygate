from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

user_bp = Blueprint('user_routes', __name__)

@user_bp.route('/user/<userId>', methods=['DELETE'])
@jwt_required()
def remove_user(userId):
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_admin_permission(current_user)

    # A user cannot delete themself.
    if current_user == userId:
        return jsonify({'message': 'Unable to remove self.'}), 400

    # Delete the user if they exist.
    db = DB()
    user_credentials = db.singleQuery("user_credentials", "username", userId)
    if userId and userId in user_credentials:
            del user_credentials[userId]
            del users_roles[userId]
    else:
        return jsonify({'message': 'User does not exists.'}), 400

    return jsonify({'message': 'User removed.'}), 200

@user_bp.route('/user', methods=['POST'])
@jwt_required()
def add_user():
    # Ensure only an authorized user accesses this endpoint.
    current_user = get_jwt_identity()
    users.check_admin_permission(current_user)

    # Get json data from the request body.
    request_body = request.json
    username = request_body.get('username')
    password = request_body.get('password')
    role = request_body.get('role')

    db = DB()
    user_credentials = db.singleQuery("user_credentials", "username", username)
    # Ensure the username doesn't already exist and the role is valid.
    if username and username not in user_credentials:
        user_credentials = db.singleQuery("user_roles", "username", username)
        if role and role in user_roles:
            db.singleInsert(user_credentials, username, password)
            db.singleInsert(users_roles, username, role)
            db.singleInsert(user_subscriptions, username, [])
        else:
            return jsonify({'message': 'Role does not exist.'}), 400
    else:
        return jsonify({'message': 'User already exists.'}), 400

    return jsonify({'message': 'User created.'}), 201
