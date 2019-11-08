apply-prod:
	terraform workspace select prod
	${eval AWS_ACCESS_KEY_ID=$${AWS_ACCESS_KEY_ID_PROD}}
	${eval AWS_SECRET_ACCESS_KEY=$${AWS_SECRET_ACCESS_KEY_PROD}}
	${eval AWS_ACCOUNT_ID=$${AWS_ACCOUNT_ID_PROD}}
	echo ${AWS_ACCOUNT_ID} && terraform apply -var-file=env.tfvars