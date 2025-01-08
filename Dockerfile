FROM nixos/nix:2.16.1

RUN nix-env -iA nixpkgs.nixFlakes && \
    echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

WORKDIR /app

COPY flake.nix .
COPY flake.lock .

RUN nix develop

ENV PATH=/env/bin:$PATH

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5555

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
