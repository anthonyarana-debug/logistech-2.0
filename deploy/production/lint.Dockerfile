FROM python:3.13.17-slim
RUN pip install --no-cache-dir cfn-lint==1.58.0
ENTRYPOINT ["cfn-lint"]
