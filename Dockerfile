FROM python:3.11

ARG EMAIL
ARG SERVER
ARG SERVER_PASS
ARG PORT

# Set the environment variables
ENV EMAIL=$EMAIL
ENV SERVER=$SERVER
ENV SERVER_PASS=$SERVER_PASS
ENV PORT=$PORT


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files into the container
COPY . .

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]