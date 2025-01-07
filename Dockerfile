FROM nixos/nix:2.16.1

RUN nix-env -iA nixpkgs.nixFlakes

WORKDIR /app

COPY flake.nix .
COPY flake.lock .

RUN nix build .#appEnv && \
    mv result /env

ENV PATH=/env/bin:$PATH

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
