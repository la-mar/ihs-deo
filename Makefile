SERVICE_NAME:=ihs
ENV:=prod
COMMIT_HASH    := $$(git log -1 --pretty=%h)
DATE := $$(date +"%Y-%m-%d")
CTX:=.
AWS_ACCOUNT_ID:=$$(aws-vault exec prod -- aws sts get-caller-identity | jq .Account -r)
# IMAGE_NAME:=driftwood/ihs
DOCKERFILE:=Dockerfile

dev:
	${eval export ENV=dev}

stage:
	${eval export ENV=stage}

prod:
	${eval export ENV=prod}

run-tests:
	pytest --cov=ihs tests/

export-deps:
	# Export dependencies from poetry to requirements.txt in the project root
	poetry export -f requirements.txt > requirements.txt --without-hashes

redis-start:
	# start a local redis container
	docker run -d --name redis -p 6379:6379 redis

init-db:
	# shortcut to initialize the database
	poetry run ihs db init

migrate:
	# shortcut for database migrations
	# poetry run ihs db stamp head
	poetry run ihs db migrate

revision:
	# Generate a new database revision file
	poetry run ihs db revision

upgrade:
	# Upgrade database version using current revisions
	poetry run ihs db upgrade

celery-worker:
	# Launch a worker process that reads from all configured queues
	chamberprod exec ihs datadog -- ihs run worker -Q ihs-default,ihs-submissions-h,ihs-collections-h,ihs-deletions-h,ihs-submissions-v,ihs-collections-v,ihs-deletions-v --loglevel DEBUG
	# Alternatively:
	# celery -E -A ihs.celery_queue.worker:celery worker --loglevel=INFO --purge


celery-beat:
	# Launch a cron process
	ihs run cron --loglevel=DEBUG
	# Alternatively
	# celery -A ihs.celery_queue.worker:celery beat --loglevel=DEBUG


celery-flower:
	# Launch a celery monitoring process using flower
	celery -A ihs.celery_queue.worker:celery flower --loglevel=DEBUG --purge

kubectl-proxy:
	# open a proxy to the configured kubernetes cluster
	kubectl proxy --port=8080


login:
	# Authenticate to ECR
	${eval export ENV_UPPER=$(shell echo ${ENV} | tr '[:lower:]' '[:upper:]')}
	@eval echo ${ENV_UPPER}
	@echo account: ${AWS_ACCOUNT_ID}
	@eval $$(aws-vault exec ${ENV} -- aws ecr get-login --no-include-email)

build:
	# initiate a build of the dockerfile specified in the DOCKERFILE environment variable
	@echo "Building docker image: ${IMAGE_NAME}"
	docker build  -f ${DOCKERFILE} ${CTX} -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${ENV}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${COMMIT_HASH}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${DATE}

push:
	docker push ${IMAGE_NAME}:latest


push-ecr:
	${eval export ECR=$(shell echo ${AWS_ACCOUNT_ID}).dkr.ecr.us-east-1.amazonaws.com}
	# @echo ${ECR}
	${eval LATEST=${IMAGE_NAME}:latest}
	${eval ECR_LATEST=${ECR}/${LATEST}}
	${eval ECR_ENV=${ECR}/${IMAGE_NAME}:$${ENV}}
	${eval ECR_HASH=${ECR}/${IMAGE_NAME}:$${COMMIT_HASH}}
	${eval ECR_DATE=${ECR}/${IMAGE_NAME}:$${DATE}}

	docker tag ${LATEST} ${ECR_LATEST}
	docker tag ${LATEST} ${ECR_ENV}
	docker tag ${LATEST} ${ECR_HASH}
	docker tag ${LATEST} ${ECR_DATE}

	docker push ${ECR_LATEST}
	docker push ${ECR_ENV}
	docker push ${ECR_HASH}
	docker push ${ECR_DATE}


create-ihs-repo:
	# Create ECR repo where repository-name = COMPOSE_PROJECT_NAME
	aws ecr create-repository --repository-name ${COMPOSE_PROJECT_NAME} --tags Key=domain,Value=technology Key=service_name,Value=${SERVICE_NAME} --profile ${ENV}

all:
	# Rebuild the services docker image and push it to the remote repository
	make ihs-deo build login push

deploy: ssm-update
	# Update SSM parameters from local dotenv and deploy a new version of the service to ECS
	${eval AWS_ACCOUNT_ID=$(shell echo ${AWS_ACCOUNT_ID})}
	@echo ${AWS_ACCOUNT_ID}
	export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID} && aws-vault exec ${ENV} -- poetry run python scripts/deploy.py

redeploy-cron:
	# Force a new deployment for the cron service through the aws cli
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-cron --force-new-deployment --profile prod

redeploy-worker:
	# Force a new deployment for the worker service through the aws cli
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-worker --force-new-deployment --profile prod

redeploy-web:
	# Force a new deployment for the web service through the aws cli
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-web --force-new-deployment --profile prod

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

view-credentials:
	# print the current temporary credentials from aws-vault
	aws-vault exec ${ENV} -- env | grep AWS

compose:
	# run docker-compose using aws-vault session credentials
	aws-vault exec prod -- docker-compose up

add-to-secret-scanner:
	git secrets --install
	git secrets --register-aws

scan-git-secrets:
	git secrets --scan-history

scan-trufflehog:
	trufflehog --regex --entropy=False --max_depth=1000 ./.git

scan-gitleaks:
	gitleaks --repo=./.git --verbose --pretty


