from flask_jwt_extended import JWTManager

class CustomJWT:
    def customErrors(self, jwt):
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
        return jwt
