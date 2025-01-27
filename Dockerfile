FROM node:18-alpine AS tailwind-builder

WORKDIR /app

COPY tailwind.config.js ./
# COPY static/css ./static/css/

RUN npm install tailwindcss
RUN npx tailwindcss -o ./static/css/output.css --minify

FROM python:3.11-slim AS python-app

WORKDIR /

COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl sudo && \
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
    dpkg -i cloudflared.deb && \
    rm cloudflared.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=tailwind-builder /app/static/css/output.css ./static/css/output.css

COPY . /

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

EXPOSE 5555

CMD ["/usr/local/bin/start.sh"]
