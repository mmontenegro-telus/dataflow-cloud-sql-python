.PHONY: help

CURRENT_DIR := $(shell basename $(CURDIR))

#DOCKER_IMAGE = gcr.io/${GCP_PROJECT_ID}/hsm-pipeline:latest
DOCKER_IMAGE = gcr.io/cio-custcntrct-d2c-np-5e35b7/pipeline-dataflow-cloud-sql-python:latest

ifneq (,$(wildcard ./.env))
    include .env
    export
    ENV_FILE_PARAM = --env-file .env
endif

help: ## Show command list
	@ grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install-dependencies: ## Install dependencies
	@ pip install apache_beam[gcp]
	@ pip install pg8000
	@ pip install psycopg2
	@ pip install sqlalchemy
	@ pip install pandas

docker-push: ## Push Dataflow docker container image to GCP
	docker build --tag ${DOCKER_IMAGE} \
		--build-arg CLOUD_SQL_INSTANCES=${CLOUD_SQL_INSTANCES} \
		--build-arg CREDENTIAL_FILE=${GCP_SERVICE_ACCOUNT_FILE} \
		--file ./devops/Dockerfile .
	docker push ${DOCKER_IMAGE}

deploy: ## Deploy pipeline template to Cloud Storage bucket
	@ python main.py \
		--runner DataflowRunner \
		--project ${GCP_PROJECT_ID} \
		--region ${GCP_REGION} \
		--input_path gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/MariaTestCSV.csv \
		--temp_location gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/tmp \
		--staging_location gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/staging/ \
		--service_account_email=d2c-dataflow-serv-acc@cio-custcntrct-d2c-np-5e35b7.iam.gserviceaccount.com \
		--subnetwork https://www.googleapis.com/compute/v1/projects/bto-vpc-host-6296f13b/regions/northamerica-northeast1/subnetworks/cio-custcntrct-d2c-dataflow \
		--network projects/bto-vpc-host-6296f13b/global/networks/bto-vpc-host-network \
		--template_location gs://cio-custcntrct-d2c-np-5e35b7-storage1/templates/test1 \
		--setup_file ./setup.py \
		--experiment=use_runner_v2 \
		--sdk_container_image=${DOCKER_IMAGE} \
		--db-url ${DB_URL}

run-local: ## Deploy pipeline template to Cloud Storage bucket
	@ python main.py \
		--runner DirectRunner \
		--project ${GCP_PROJECT_ID} \
		--region ${GCP_REGION} \
		--input_path gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/MariaTestCSV.csv \
		--temp_location gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/tmp \
		--staging_location gs://cio-custcntrct-d2c-np-5e35b7-storage1/dataflow/staging/ \
		--service_account_email=d2c-dataflow-serv-acc@cio-custcntrct-d2c-np-5e35b7.iam.gserviceaccount.com \
		--subnetwork https://www.googleapis.com/compute/v1/projects/bto-vpc-host-6296f13b/regions/northamerica-northeast1/subnetworks/cio-custcntrct-d2c-dataflow \
		--network projects/bto-vpc-host-6296f13b/global/networks/bto-vpc-host-network