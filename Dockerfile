FROM python:3.9.7
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENTRYPOINT [ "python3", "-m", "foldergram" ]