FROM python:latest
#todo: change to NIX

WORKDIR /

#install python libraries
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

RUN apt-get update && apt-get install -y curl sudo && \
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && \
    dpkg -i cloudflared.deb && \
    rm cloudflared.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /

EXPOSE 5555

#run server
# TODO: change port to variable

# Use the script as the CMD
CMD ["/usr/local/bin/start.sh"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
