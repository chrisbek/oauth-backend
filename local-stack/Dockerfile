FROM serverless_base:0.0.2 as base

WORKDIR /frontend_service
COPY ./package-lock.json ./package-lock.json ./pyproject.toml ./poetry.lock /frontend_service/
RUN npm install
RUN apt-get update && apt-get install -y openssh-client
RUN mkdir -p -m 0600 /root/.ssh/ && ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN --mount=type=ssh GIT_SSH_COMMAND="ssh -vvvT" pip3 install -r requirements.txt --no-cache
COPY ./serverless.yml.local /frontend_service/
RUN cp serverless.yml.local serverless.yml -v