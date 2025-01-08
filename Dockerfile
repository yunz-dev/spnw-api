FROM python:latest

WORKDIR /

#install python libraries
COPY requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

COPY . /


EXPOSE 5555

#run server
# TODO: chnage port to variable
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555"]
