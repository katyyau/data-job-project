FROM python:3.10

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt update && apt install -y ./google-chrome-stable_current_amd64.deb

COPY double-genius-331713-53d701549c5b.json double-genius-331713-53d701549c5b.json

COPY app.py app.py

CMD ["python3", "app.py"]