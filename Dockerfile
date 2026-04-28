FROM python:3.11-slim

# System dependencies (for scapy/pyshark live capture + nmap)
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    nmap \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything (models, pages, scripts, etc.)
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "main_app.py", \
  "--server.port=8501", \
  "--server.address=0.0.0.0", \
  "--server.headless=true"]
