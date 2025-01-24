FROM public.ecr.aws/lambda/python:3.10

# change this as per your requirements
# but directory in s3 bucket should follow this structure

# {RESULT_OBJECT_KEY}/
# └── transcription_results/

ENV RESULT_BUCKET_NAME=revocalize-files
ENV RESULT_OBJECT_KEY=results

# Combine all necessary commands
RUN yum install -y tar xz wget && \
    mkdir -p /var/task/ffmpeg && \
    cd /var/task/ffmpeg && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/* . && \
    rm -rf ffmpeg-*-amd64-static ffmpeg-release-amd64-static.tar.xz && \
    chmod -R +x /var/task/ffmpeg

ENV PATH="/var/task/ffmpeg:${PATH}"

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir ffmpeg-python -t /var/task && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Whisper model (consider runtime download or external storage for smaller image size)
RUN python ${LAMBDA_TASK_ROOT}/whisper_manager.py --model_name small --root ${LAMBDA_TASK_ROOT}/.cache/whisper
ENV WHISPER_MODEL=${LAMBDA_TASK_ROOT}/.cache/whisper/small.pt

CMD [ "lambda_function.lambda_handler" ]
