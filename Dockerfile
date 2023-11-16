FROM python:3.10-bullseye
LABEL for="automata-simulator"

WORKDIR /usr/sim/
COPY requirements-ipynb.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements-ipynb.txt

COPY . .

CMD [ "/bin/bash" ]