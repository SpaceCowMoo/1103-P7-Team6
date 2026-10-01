FROM python:3.11-slim

WORKDIR /app/OpportunityFit

COPY *.py ./

CMD [ "python", "app.py" ]