FROM python:3.10-bullseye
LABEL for="automata-simulator"

WORKDIR /usr/sim/
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD [ "/bin/bash" ]