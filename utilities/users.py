class users:
    def check_user_role_access_api(current_user, apiKey):
        user_role = ''
        if current_user in users_roles:
            user_role = users_roles[current_user]
        if user_role not in api_user_roles[apiKey]:
            return jsonify({'message': 'User role does not have access to this API.'}), 403

    def check_admin_endpoint(current_user):
        user_role = ''
        if current_user in users_roles:
            user_role = users_roles[current_user]
        if user_role != 'admin':
            return jsonify({'message': 'You do not have permission to access this endpoint.'}), 403
