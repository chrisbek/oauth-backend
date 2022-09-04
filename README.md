# OAuth-Backend
Read the full docs at: [authentication-as-a-service](https://christopher.bekos.click/portfolio/authentication-as-a-service).

This service exposes several endpoints that are necessary in order to implement the Authorization Code Grant of the OAuth 2.0 
protocol.
It provides a secure way for to exchange tokens with a Frontend, protecting from the following attacks:
- CSRF attack
- XSS attack

This service should be used together with other microservices, as you can read in the full docs.

## Technologies used
- `FastAPI`: for the api creation
- `Poetry`: for dependency management
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/) for dependency injection, singleton pattern
implementation, and project structure.
- `DynamoDB` for temporary session identifiers storage.
- `Docker` and `DockerComposer` for containerization.


## Local Setup
- Clone the [local-stack](https://github.com/chrisbek/local-stack).
  - Start a local DynamoDB server by running:
    ```
    make start-databases
    ```
  - Start a reverse-proxy server by running:
    ```
    make start-nginx
    ```
  
- Add the following line to your `/etc/hosts`:
```
172.30.0.8	dynamodb.local
172.30.1.0	authentication.local
```

- Start the service:
```
cd local-stack
./stack-run.sh
```
