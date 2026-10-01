FROM python:3.11-slim

WORKDIR /app/OpportunityFit

# Create the folder for CSV to be saved
RUN mkdir -p /app/OpportunityFit/data

# Copy all project files into the container
COPY . .

# Declare the data folder as a volume mount point
VOLUME ["/app/OpportunityFit/data"]

CMD [ "python", "app.py" ]