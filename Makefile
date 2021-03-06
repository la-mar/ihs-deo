SERVICE_NAME := ihs
ENV ?= prod
COMMIT_HASH := $$(git log -1 --pretty=%h)
DATE := $$(date +"%Y-%m-%d")
CTX?=.
AWS_ACCOUNT_ID ?= $$(aws-vault exec prod -- aws sts get-caller-identity | jq .Account -r)
IMAGE_NAME ?= driftwood/ihs
DOCKERFILE ?= Dockerfile
APP_VERSION ?= $$(grep -o '\([0-9]\+.[0-9]\+.[0-9]\+\)' pyproject.toml | head -n1)

run-web:
	aws-vault exec ${ENV} -- docker run -e AWS_REGION -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN -e AWS_SECURITY_TOKEN -p 8000:5000 driftwood/ihs ihs run web

run-tests:
	pytest --cov=ihs tests/ --cov-report xml:./coverage/python/coverage.xml

smoke-test:
	docker run --entrypoint ihs driftwood/ihs:${COMMIT_HASH} test smoke-test

coverage:
	pytest --cov ihs --cov-report html:./coverage/coverage.html --log-level DEBUG

view-cov:
	open -a "Google Chrome" ./coverage/coverage.html/index.html

release:
	poetry run python scripts/release.py

export-deps:
	# Export dependencies from poetry to requirements.txt in the project root
	poetry export -f requirements.txt > requirements.txt --without-hashes

profile-submitter:
	mprof aws-vault exec prod -- ihs run worker -Q ihs-submissions-h,ihs-submissions-v --loglevel DEBUG

login:
	docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}

build:
	@echo "Building docker image: ${IMAGE_NAME}"
	docker build  -f Dockerfile . -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:${APP_VERSION}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:latest


build-with-chamber:
	@echo "Building docker image: ${IMAGE_NAME} (with chamber)"
	docker build  -f Dockerfile.chamber . -t ${IMAGE_NAME}
	# docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-${COMMIT_HASH}
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-${APP_VERSION}
	# docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-dev
	docker tag ${IMAGE_NAME} ${IMAGE_NAME}:chamber-latest

build-all: build-with-chamber build

push: login
	# docker push ${IMAGE_NAME}:dev
	# docker push ${IMAGE_NAME}:${COMMIT_HASH}
	docker push ${IMAGE_NAME}:latest

push-all: login push
	# docker push ${IMAGE_NAME}:chamber-dev
	# docker push ${IMAGE_NAME}:chamber-${COMMIT_HASH}
	docker push ${IMAGE_NAME}:chamber-latest

push-version:
	# docker push ${IMAGE_NAME}:latest
	@echo pushing: ${IMAGE_NAME}:${APP_VERSION}, ${IMAGE_NAME}:chamber-${APP_VERSION}
	docker push ${IMAGE_NAME}:${APP_VERSION}
	docker push ${IMAGE_NAME}:chamber-${APP_VERSION}

all: build push

cc-expand:
	# show expanded configuration
	circleci config process .circleci/config.yml

cc-process:
	circleci config process .circleci/config.yml > process.yml

cc-run-local:
	JOBNAME?=build-image
	circleci local execute -c process.yml --job build-image -e DOCKER_LOGIN=${DOCKER_LOGIN} -e DOCKER_PASSWORD=${DOCKER_PASSWORD}

deploy:
	# Update SSM parameters from local dotenv and deploy a new version of the service to ECS
	${eval AWS_ACCOUNT_ID=$(shell echo ${AWS_ACCOUNT_ID})}
	@echo ${AWS_ACCOUNT_ID}
	export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID} && aws-vault exec ${ENV} -- poetry run python scripts/deploy.py

redeploy-cron:
	@echo ""
	aws ecs update-service --cluster ${ECS_COLLECTOR_CLUSTER} --service ihs-cron --force-new-deployment --profile ${ENV} | jq .service.serviceName,.service.taskDefinition,.service.clusterArn

redeploy-worker:
	@echo ""
	aws ecs update-service --cluster ${ECS_COLLECTOR_CLUSTER} --service ihs-worker-default --force-new-deployment --profile ${ENV} | jq .service.serviceName,.service.taskDefinition,.service.clusterArn

	@echo ""
	aws ecs update-service --cluster ${ECS_COLLECTOR_CLUSTER} --service ihs-worker-submitter --force-new-deployment --profile ${ENV} | jq .service.serviceName,.service.taskDefinition,.service.clusterArn

	@echo ""
	aws ecs update-service --cluster ${ECS_COLLECTOR_CLUSTER} --service ihs-worker-collector --force-new-deployment --profile ${ENV} | jq .service.serviceName,.service.taskDefinition,.service.clusterArn

redeploy-web:
	@echo ""
	aws ecs update-service --cluster ${ECS_WEB_CLUSTER} --service ihs-web --force-new-deployment --profile ${ENV} | jq .service.serviceName,.service.taskDefinition,.service.clusterArn

redeploy: redeploy-worker redeploy-cron redeploy-web

ssm-export:
	# Export all SSM parameters associated with this service to json
	aws-vault exec ${ENV} -- chamber export ${SERVICE_NAME} | jq

ssm-export-dotenv:
	# Export all SSM parameters associated with this service to dotenv format
	aws-vault exec ${ENV} -- chamber export --format=dotenv ${SERVICE_NAME} | tee .env.ssm

env-to-json:
	# pipx install json-dotenv
	python3 -c 'import json, os, dotenv;print(json.dumps(dotenv.dotenv_values(".env.production")))' | jq

ssm-update:
	# Update SSM environment variables using a local dotenv file (.env.production by default)
	python3 -c 'import json, os, dotenv; values={k.lower():v for k,v in dotenv.dotenv_values(".env.production").items()}; print(json.dumps(values))' | jq | aws-vault exec ${ENV} -- chamber import ${SERVICE_NAME} -

ssm:
	chamber export ${SERVICE_NAME} | jq
	chamber export ${SERVICE_NAME}-worker | jq
	chamber export ${SERVICE_NAME}-cron | jq
	chamber export ${SERVICE_NAME}-web | jq

view-credentials:
	# print the current temporary credentials from aws-vault
	aws-vault exec ${ENV} -- env | grep AWS

compose:
	# run docker-compose using aws-vault session credentials
	aws-vault exec ${ENV} -- docker-compose up


send-request:
	http :5001/well/h/42461409160000
	http :5001/well/h/42383406370000
	http :5001/well/h/42461412100000