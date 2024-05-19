FROM python:3.12-slim
WORKDIR /app

RUN apt-get update \
    && apt-get install -y  --no-install-recommends dvipng texlive-latex-base texlive-latex-extra \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --break-system-packages --no-cache-dir .

CMD notabot $(cat /run/secrets/notabot-token)
