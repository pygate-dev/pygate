from pymongo import MongoClient

class DB:
    def getMongoDB(self):
        try:
            client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=1000)
            return client
        except Exception as e:
            raise MongoConnectionError("MongoDB is not started.") from e

    def singleQuery(self, db, table, value):
        data = None
        query_collection = db["pygate"]
        document = query_collection.find_one({table: value})
        return data

    def initializeMongoDB(self):
        client = self.getMongoDB()
        db = client['pygate']
        # Check if collection already exists.
        collection_list = db.list_collection_names()
        if "user_credentials" in collection_list:
            print("pygate | Database already initialized.")
            return

        # Create tables
        user_credentials = db.create_collection('user_credentials')
        user_roles = db.create_collection('user_roles')
        users_roles = db.create_collection('users_roles')
        user_subscriptions = db.create_collection('user_subscriptions')
        api_keys = db.create_collection('api_keys')
        api_contexts = db.create_collection('api_contexts')
        api_backends = db.create_collection('api_backends')
        api_backend_rotation = db.create_collection('api_backend_rotation')
        api_endpoints = db.create_collection('api_endpoints')
        api_backend_api_endpoint = db.create_collection('api_backend_api_endpoint')
        api_user_roles = db.create_collection('api_user_roles')
        unhealthy_apis = db.create_collection('unhealthy_apis')
        unhealthy_urls = db.create_collection('unhealthy_urls')

        # Define indexes.
        user_credentials.create_index([('username', 1)], unique=True)
        user_roles.create_index([('role', 1)], unique=True)
        users_roles.create_index([('username', 1)], unique=True)
        user_subscriptions.create_index([('username', 1)], unique=True)
        api_keys.create_index([('api_context', 1)], unique=True)
        api_contexts.create_index([('apiKey', 1)], unique=True)
        api_backends.create_index([('apiKey', 1)], unique=True)
        api_backend_rotation.create_index([('api_key', 1)], unique=True)
        api_endpoints.create_index([('api_key', 1)], unique=True)
        api_backend_api_endpoint.create_index([('api_key', 1)], unique=True)
        api_user_roles.create_index([('apiKey', 1)], unique=True)
        unhealthy_apis.create_index([('apiKey', 1)], unique=True)
        unhealthy_urls.create_index([('apiKey', 1)], unique=True)

        user_credentials.insert_one({ "username": "admin", "password": "password" })
        user_roles.insert_one({ "admin": ""})
        users_roles.insert_one({ "admin": "admin"})

        print("pygate | Database initialization successful.")
