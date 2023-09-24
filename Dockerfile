FROM python:3.11-slim
COPY poetry.lock /app/poetry.lock
COPY pyproject.toml /app/pyproject.toml
RUN poetry install --no-cache-dir -r requirements.txt
#COPY . .
#CMD [ "python", "./your-daemon-or-script.py" ]
#EXPOSE 8080
#
