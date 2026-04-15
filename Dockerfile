FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias base y el driver de SQL Server
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    gnupg \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código y la carpeta de agentes
COPY server.py .
COPY agents/ agents/

EXPOSE 8000

# El server.py ahora maneja el host 0.0.0.0 internamente con uvicorn.run
CMD ["python", "server.py"]