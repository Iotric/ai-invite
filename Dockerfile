FROM public.ecr.aws/lambda/python:3.10

# change this as per your requirements
# but directory in s3 bucket should follow this structure

# {RESULT_OBJECT_KEY}/
# └── video_processing_results/
#     ├── extracted_audios/
#     └── updated_videos/

ENV RESULT_BUCKET_NAME=revocalize-files
ENV RESULT_OBJECT_KEY=results

# Install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . ${LAMBDA_TASK_ROOT}

CMD [ "lambda_function.lambda_handler" ]