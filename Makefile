SERVICE_NAME:=ihs
ENV:=prod
COMMIT_HASH    := $$(git log -1 --pretty=%h)
DATE := $$(date +"%Y-%m-%d")
CTX:=.

dev:
	${eval export ENV=dev}

stage:
	${eval export ENV=stage}

prod:
	${eval export ENV=prod}

ihs-deo:
	${eval export DOCKERFILE=Dockerfile}

export-deps:
	poetry export -f requirements.txt > requirements.txt --without-hashes

redis-start:
	docker run -d --name redis -p 6379:6379 redis

init-db:
	poetry run ihs db init

migrate:
	# poetry run ihs db stamp head
	poetry run ihs db migrate

revision:
	poetry run ihs db revision

upgrade:
	poetry run ihs db upgrade

celery-worker:
	# celery -E -A ihs.celery_queue.worker:celery worker --loglevel=INFO --purge
	ihs run worker -Q ihs-default,ihs-submissions-h,ihs-collections-h,ihs-deletions-h,ihs-submissions-v,ihs-collections-v,ihs-deletions-v --loglevel DEBUG

celery-beat:
	# celery -A ihs.celery_queue.worker:celery beat --loglevel=DEBUG
	ihs run cron --loglevel=DEBUG

celery-flower:
	celery -A ihs.celery_queue.worker:celery flower --loglevel=DEBUG --purge

ihs-start:
	poetry run ihs ipython

kubectl-proxy:
	kubectl proxy --port=8080

build:
	@echo "Building docker image: ${IMAGE_NAME}"
	docker build  -f ${DOCKERFILE} ${CTX} -t ${IMAGE_NAME}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${ENV}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${COMMIT_HASH}
	docker tag ${IMAGE_NAME}:latest ${IMAGE_NAME}:${DATE}

login:
	${eval export ENV_UPPER=$(shell echo ${ENV} | tr '[:lower:]' '[:upper:]')}
	@eval echo ${ENV_UPPER}
	${eval export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID_${ENV_UPPER}}}
	${eval export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID_${ENV_UPPER}}}
	${eval export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY_${ENV_UPPER}}}
	@eval echo deploy environment: ${ENV_UPPER} - ${AWS_ACCOUNT_ID}
	@echo account: ${AWS_ACCOUNT_ID}
	@eval $$(aws ecr get-login --no-include-email)

create-ihs-repo:
	aws ecr create-repository --repository-name ${COMPOSE_PROJECT_NAME} --tags Key=domain,Value=technology Key=service_name,Value=${SERVICE_NAME} --profile ${ENV}


all:
	make ihs-deo build login push

deploy: ssm-update
	poetry run python scripts/deploy.py

push:
	${eval export ECR=${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com}
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

redeploy-cron:
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-cron --force-new-deployment --profile prod

redeploy-worker:
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-worker --force-new-deployment --profile prod

redeploy-web:
	aws ecs update-service --cluster ${ECS_CLUSTER}-prod --service ihs-web --force-new-deployment --profile prod

ssm-export:
	aws-vault exec ${ENV} -- chamber export ${SERVICE_NAME} | jq

ssm-export-dotenv:
	aws-vault exec ${ENV} -- chamber export --format=dotenv ${SERVICE_NAME}

env-to-json:
	# pipx install json-dotenv
	python3 -c 'import json, os, dotenv;print(json.dumps(dotenv.dotenv_values(".env.production")))' | jq

ssm-update:
	python3 -c 'import json, os, dotenv;print(json.dumps(dotenv.dotenv_values(".env.production")))' | jq | aws-vault exec ${ENV} -- chamber import ihs -

view-credentials:
	aws-vault exec ${ENV} -- env | grep AWS

compose:
	aws-vault exec prod -- docker-compose up
