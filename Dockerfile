# Use an official Python runtime as the base image
FROM python:3.9-slim  

# Set the working directory in the container
WORKDIR /app  

# Copy the requirements file into the container
COPY requirements.txt .  

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# Copy the project files into the container
COPY . .  

# Set the AIPROXY_TOKEN environment variable (but don't hardcode the value)
ARG AIPROXY_TOKEN  
ENV AIPROXY_TOKEN=${AIPROXY_TOKEN}  

# Create the /data directory
RUN mkdir /data  

# Expose the port that FastAPI will run on
EXPOSE 8000  

# Run FastAPI with the correct module path
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
