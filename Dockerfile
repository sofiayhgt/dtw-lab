# matches requires-python = ">=3.12,<3.13"
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install .

EXPOSE 80

CMD ["start-server"]