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
	${eval export IMAGE_NAME=ihs-deo}

export-deps:
	poetry export -f requirements.txt > requirements.txt --without-hashes

redis-start:
	docker run -d --name redis -p 6379:6379 redis

init-db:
	poetry run app db init

migrate:
	# poetry run app db stamp head
	poetry run app db migrate

revision:
	poetry run app db revision

upgrade:
	poetry run app db upgrade

celery-worker:
	celery -E -A app.celery_queue.worker:celery worker --loglevel=INFO --purge

celery-beat:
	celery -A app.celery_queue.worker:celery beat --loglevel=DEBUG

celery-flower:
	celery -A app.celery_queue.worker:celery flower --loglevel=DEBUG --purge

app-start:
	poetry run app ipython

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
	aws ecr create-repository --repository-name ${COMPOSE_PROJECT_NAME} --tags Key=domain,Value=technology Key=service_name,Value=ihs --profile ${ENV}


all:
	make ihs-deo build login push

deploy:
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

redeploy:
	aws ecs update-service --cluster ${ECS_CLUSTER} --service ${COMPOSE_PROJECT_NAME} --force-new-deployment

aws-ps-test:
	@echo $$(aws ssm get-parameter --name datadog_api_key | jq '.Parameter.Value')