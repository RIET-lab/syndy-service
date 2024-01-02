FROM python:3.8-slim

COPY *.py *.txt ./
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "--timeout", "2400", "index:app"]
