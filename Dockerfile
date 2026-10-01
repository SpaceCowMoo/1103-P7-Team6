FROM python:3.11-slim

WORKDIR /app/OpportunityFit

# Create the folder for CSV to be saved
RUN mkdir -p /app/OpportunityFit/data

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Declare the data folder as a volume mount point
VOLUME ["/app/OpportunityFit/data"]

CMD [ "python", "app.py" ]