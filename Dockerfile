FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y tar xz wget

RUN mkdir -p /var/task/ffmpeg && \
    cd /var/task/ffmpeg && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/* . && \
    rm -rf ffmpeg-*-amd64-static && \
    rm ffmpeg-release-amd64-static.tar.xz

ENV PATH="/var/task/ffmpeg:${PATH}"

RUN chmod -R +x /var/task/ffmpeg

RUN pip install ffmpeg-python -t /var/task

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY /** ${LAMBDA_TASK_ROOT}

RUN python ${LAMBDA_TASK_ROOT}/whisper_manager.py --model_name small --root ${LAMBDA_TASK_ROOT}/.cache

# Set environment variable for WHISPER_MODEL
ENV WHISPER_MODEL=${LAMBDA_TASK_ROOT}/.cache/small.pt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ]