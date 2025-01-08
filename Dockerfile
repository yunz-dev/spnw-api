FROM python:latest

WORKDIR /

COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY . /

EXPOSE 5555

#run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
