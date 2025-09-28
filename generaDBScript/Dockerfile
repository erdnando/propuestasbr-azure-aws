FROM python:3.11-slim

ENV ACCEPT_EULA=Y
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg2 ca-certificates \
    && mkdir -p /usr/share/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
    && apt-get install -y --no-install-recommends unixodbc unixodbc-dev gcc g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/mssql-tools18/bin:${PATH}"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "app.main"]
CMD ["generate", "-c", "config/example_config.yml"]
