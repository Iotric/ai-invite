FROM public.ecr.aws/lambda/python:3.10

# Combine all necessary commands
RUN yum install -y tar xz wget unzip libsndfile.x86_64 && \
    # Install FFmpeg
    mkdir -p ${LAMBDA_TASK_ROOT}/ffmpeg && \
    cd ${LAMBDA_TASK_ROOT}/ffmpeg && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xvf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/* . && \
    rm -rf ffmpeg-*-amd64-static ffmpeg-release-amd64-static.tar.xz && \
    chmod -R +x ${LAMBDA_TASK_ROOT}/ffmpeg && \
    # Install Hugging Face models
    mkdir -p ${LAMBDA_TASK_ROOT}/.hf_cache/vocos && \
    mkdir -p ${LAMBDA_TASK_ROOT}/.hf_cache/f5tts && \
    cd ${LAMBDA_TASK_ROOT}/.hf_cache/vocos && \
    # Download vocos-mel-24khz
    wget https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/config.yaml && \
    wget https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin && \
    cd ${LAMBDA_TASK_ROOT}/.hf_cache/f5tts && \
    # Download F5-TTS Model checkpoints
    wget https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/vocab.txt && \
    wget https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.safetensors && \
    # Install AWS CLI
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws && \
    yum remove -y unzip && \
    yum clean all && \
    rm -rf /var/cache/yum

# Set environment variables
ENV PATH="${LAMBDA_TASK_ROOT}/ffmpeg:${PATH}"
ENV VOCOS_FOLDER=${LAMBDA_TASK_ROOT}/.hf_cache/vocos
ENV CLONER_VOCAB=${LAMBDA_TASK_ROOT}/.hf_cache/f5tts/vocab.txt
ENV CLONER_CKPT=${LAMBDA_TASK_ROOT}/.hf_cache/f5tts/model_1200000.safetensors

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to handler 
CMD [ "lambda_function.lambda_handler" ]