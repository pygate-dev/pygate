
![Logo](https://i.ibb.co/Y5T8g9y/pygate-logo-white.png)

##

One Platform for AI, REST, SOAP, GraphQL, gRPC and Websocket APIs. Fully managed with its own set of RESTful APIs. This is your APIs gateway to the world!

🔗 [pygate.org](https://pygate.org)

No specialized low-level langauge expertise required. Just a simple, cost-effective API Gateway built in Python. Keep it simple, scalable, and efficient while giving developers everything they need to manage APIs with ease. 🐍

## ✅ MVP Roadmap 🚀
- [x]  Gateway Authentication.
- [x]  Basic user management.
- [x]  API subscriptions.
- [x]  Basic Authorization (user roles and groups).
- [x]  REST gateway implementation.
- [ ]  Basic logging (in progress ⏳).
- [ ]  Advanced user management (rate limiting and throttling).
- [ ]  Advanced Authorization (role and group permissions).
- [ ]  Key based routing
- [ ]  Code optimization and testing.
- [ ]  Add REST capabilties to user documentation.
- [ ]  Version 1.0.0 release.
- [ ]  AI gatewat implementation.
- [ ]  Code optimization and testing.
- [ ]  Add AI capabilties to user documentation.
- [ ]  Version 1.1.0 release.
- [ ]  GraphQL gateway implementation.
- [ ]  Code optimization and testing.
- [ ]  Add GraphQL capabilties to user documentation.
- [ ]  Version 1.2.0 release.
- [ ]  gRPC gateway implementation.
- [ ]  Code optimization and testing.
- [ ]  Add gRPC capabilties to user documentation.
- [ ]  Version 1.3.0 release.
- [ ]  Websockets gateway implementation.
- [ ]  Code optimization and testing.
- [ ]  Add Websockets capabilties to user documentation.
- [ ]  Version 1.4.0 release.
- [ ]  Improve caching.
- [ ]  Advanced logging.
- [ ]  Enable field encryption.
- [ ]  Refactor codebase.
- [ ]  Improve user documentation.
- [ ]  Version 1.5.0 release.



## Installation

Ensure you have a MongoDB server and redis running.

Install requirements

```bash
  pip install -r requirements.txt
```

Set environment variables
```bash
MONGO_DB_URI=mongodb://localhost:27017/pygate

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

JWT_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

ALLOWED_ORIGINS=http://localhost:5001
ALLOW_CREDENTIALS=true
ALLOW_METHODS=GET,POST,PUT,DELETE
ALLOW_HEADERS=*

ENV=dev
PORT=5001
HTTPS_ONLY=False
COOKIE_DOMAIN=localhost

PID_FILE=pygate.pid
```

Start pygate
    
```bash
  python pygate.py start
```

Stop pygate
    
```bash
  python pygate.py stop
```

Run pygate in console
    
```bash
  python pygate.py run
```



## License Information

The contents of this repository are property of pygate.org.

Review the Apache License 2.0 for valid authorization of use.

[View License - Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)



## Disclaimer

Use this code at your own risk. All liability is disclaimed.

This code is not yet ready for production environments.

Using this project you agree to the terms and conditions set forth in the license and noted annotations in the code.
