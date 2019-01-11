FROM python:3.6-alpine

COPY . /app
WORKDIR /app
RUN pip install -e .

EXPOSE 5000

CMD ["python", "blockchain.py"]
