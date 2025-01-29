#!/bin/bash
# initial setup needed before it
# aws configuration
# docker desktop or daemon running
ACCOUNT_ID=""
IMAGE_NAME="video-audio-separation"
# build docker image at local
docker build -t ${IMAGE_NAME}  .
# docker cli to aws ecr registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com
# create ECR repository  || if repository already exist skip it
aws ecr create-repository --repository-name ${IMAGE_NAME} --region us-east-1 --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
# create docker image  same as name of reposity
docker tag ${IMAGE_NAME} ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${IMAGE_NAME}:latest
# push the local image to the aws ecr repository
docker push ${ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${IMAGE_NAME}:latest






