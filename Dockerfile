FROM python:slim
ENV PYTHONUNBUFFERED=1
ENV	PYTHONDONTWRITEBYTECODE=1
WORKDIR /opt/app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY polls_test_service .
