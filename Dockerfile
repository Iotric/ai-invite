FROM public.ecr.aws/lambda/python:3.10

# Combine all necessary commands
RUN yum install -y  wget && \
    mkdir -p ${LAMBDA_TASK_ROOT}/.hf_cache/vocos && \
    mkdir -p ${LAMBDA_TASK_ROOT}/.hf_cache/f5tts && \
    cd ${LAMBDA_TASK_ROOT}/.hf_cache/vocos && \
    wget https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/config.yaml && \
    wget https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin && \
    cd ${LAMBDA_TASK_ROOT}/.hf_cache/f5tts && \
    wget https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/vocab.txt && \
    wget https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.safetensors

ENV VOCOS_FOLDER=${LAMBDA_TASK_ROOT}/.hf_cache/vocos
ENV F5TTS_VOCAB=${LAMBDA_TASK_ROOT}/.hf_cache/f5tts/vocab.txt
ENV F5TTS_CKPT=${LAMBDA_TASK_ROOT}/.hf_cache/f5tts/model_1200000.safetensors

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.lambda_handler" ]