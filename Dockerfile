FROM python:3-alpine 

LABEL maintainer="rhelins@sandia.gov"

COPY . /src/

WORKDIR /src

RUN pip install -r /src/requirements.txt

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
