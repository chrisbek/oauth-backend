#!/bin/sh
set -e

if ! [ -e poetrylocal.sha1 ]
then
    sha1sum ../poetry.lock > poetrylocal.sha1
fi
if ! [ -e packagelock.sha1 ]
then
    sha1sum ../package-lock.json > packagelock.sha1
fi
if ! [ -e serverlessyml.sha1 ]
then
    sha1sum ../serverless.yml.local > serverlessyml.sha1
fi

rebuild_required=false
package_lock_checksum_unmodified=$(echo $(cat ./packagelock.sha1 | sha1sum -c 2>&1 | grep 'OK' -c))
if [ $package_lock_checksum_unmodified = 0 ]; then
  rebuild_required=true
fi
poetry_lock_checksum_unmodified=$(echo $(cat ./poetrylocal.sha1 | sha1sum -c 2>&1 | grep 'OK' -c))
if [ $poetry_lock_checksum_unmodified = 0 ]; then
  rebuild_required=true
fi
serverless_checksum_unmodified=$(echo $(cat ./serverlessyml.sha1 | sha1sum -c 2>&1 | grep 'OK' -c))
if [ $serverless_checksum_unmodified = 0 ]; then
  rebuild_required=true
fi

# rebuild image if necessary
if [ $rebuild_required = "true" ]; then
  eval $(ssh-agent)
  ssh-add ~/.ssh/bitbucketkey
  DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker build -t frontend-service:base -f ./Dockerfile --ssh default=${SSH_AUTH_SOCK} ../
fi

# start docker-compose
docker-compose -p frontend-service -f ./docker-compose.yaml up -d