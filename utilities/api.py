class API:
    def check_api_exists(apiKey):
        return apiKey in api_contexts

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
