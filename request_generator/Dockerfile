FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the Python script
COPY request_generator.py .

# Install pymongo
RUN pip install pymongo cherrypy requests numpy

# Run the script
CMD ["python", "request_generator.py"]