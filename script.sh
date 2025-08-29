#!/bin/bash

IMAGE_NAME="idrisniyi94/nia-deployment"
# Generate a unique tag based on the current date and time
IMAGE_TAG="nia-$(date +%Y%m%d%H%M%S)"
CONTAINER_NAME="nia"

# Step 0: Pre-deployment updates
echo "========================================"
echo "Starting pre-deployment updates..."
echo "========================================"

# Update system packages
echo "Updating system packages..."
sudo apt-get update -y
if [ $? -ne 0 ]; then
    echo "Warning: System update failed, continuing with deployment..."
fi

# Pull latest changes from git (if in a git repository)
if [ -d ".git" ]; then
    echo "Pulling latest changes from git repository..."
    git fetch origin
    if [ $? -eq 0 ]; then
        CURRENT_BRANCH=$(git branch --show-current)
        echo "Current branch: $CURRENT_BRANCH"
        git pull origin $CURRENT_BRANCH
        if [ $? -eq 0 ]; then
            echo "Git pull successful."
        else
            echo "Warning: Git pull failed, continuing with current code..."
        fi
    else
        echo "Warning: Git fetch failed, continuing with current code..."
    fi
else
    echo "No git repository found, skipping git operations..."
fi

# Update Python dependencies if virtual environment exists
if [ -d "venv" ]; then
    echo "Updating Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    if [ $? -eq 0 ]; then
        echo "Python dependencies updated successfully."
    else
        echo "Warning: Python dependency update failed, continuing..."
    fi
    deactivate
else
    echo "No virtual environment found, skipping Python updates..."
fi

# Update Docker if it exists
if command -v docker &> /dev/null; then
    echo "Updating Docker images..."
    docker system prune -f
    echo "Docker cleanup completed."
else
    echo "Docker not found, skipping Docker updates..."
fi

echo "========================================"
echo "Pre-deployment updates completed!"
echo "Starting deployment process..."
echo "========================================"

# Step 1: Build the Docker image
echo "========================================"
echo "Building Docker image..."
echo "========================================"
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed!"
    exit 1
fi
echo "Docker image built successfully: ${IMAGE_NAME}:${IMAGE_TAG}"

# Step 2: Push the Docker image to Docker Hub
echo "========================================"
echo "Pushing Docker image to Docker Hub..."
echo "========================================"
docker push ${IMAGE_NAME}:${IMAGE_TAG}
if [ $? -ne 0 ]; then
    echo "Error: Docker push failed!"
    exit 1
fi
echo "Docker image pushed successfully to Docker Hub."

# Step 3: Check if the container is already running
echo "========================================"
echo "Checking for existing container..."
echo "========================================"
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping and removing the running container..."
    docker stop ${CONTAINER_NAME}
    docker rm ${CONTAINER_NAME}
    # Remove old images with the same pattern
    OLD_IMAGES=$(docker images -q ${IMAGE_NAME}:nia-* | head -n -1)
    if [ ! -z "$OLD_IMAGES" ]; then
        echo "Removing old images..."
        docker rmi $OLD_IMAGES || true
    fi
    echo "Old container stopped and removed successfully."
else
    echo "No running container found with the name ${CONTAINER_NAME}."
fi

# Step 4: Run the Docker container
echo "========================================"
echo "Starting new Docker container..."
echo "========================================"

# Update only the nia_namecheap service image in compose.yaml
awk -v new_image="${IMAGE_NAME}:${IMAGE_TAG}" '
    BEGIN {in_service=0}
    /^services:/ {in_service=1}
    in_service && /^  nia_namecheap:/ {nia=1}
    nia && /^    image:/ {
        print "    image: " new_image; nia=0; next
    }
    {print}
' compose.yaml > compose.yaml.tmp && mv compose.yaml.tmp compose.yaml
echo "Updated nia_namecheap image in compose.yaml to: ${IMAGE_TAG}"

# Start the container using docker-compose
docker compose up -d --build
if [ $? -ne 0 ]; then
    echo "Error: Failed to start container with docker-compose!"
    exit 1
fi
echo "Container started successfully with docker-compose."

# Step 5: Verify that the container is running
echo "========================================"
echo "Verifying deployment..."
echo "========================================"
sleep 5  # Wait a moment for the container to fully start

if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "✅ Container ${CONTAINER_NAME} is running successfully!"
    
    # Get container information
    echo ""
    echo "Container Details:"
    docker ps -f name=${CONTAINER_NAME} --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Check container logs for any immediate errors
    echo ""
    echo "Recent container logs:"
    docker logs --tail 10 ${CONTAINER_NAME}
    
else
    echo "❌ Failed to run the container ${CONTAINER_NAME}."
    echo "Checking docker-compose logs for errors..."
    docker compose logs --tail 20
    exit 1
fi

# Final deployment summary
echo ""
echo "========================================"
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉"
echo "========================================"
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Container: ${CONTAINER_NAME}"
echo "Deployment time: $(date)"
echo ""
echo "To check logs: docker logs ${CONTAINER_NAME}"
echo "To stop: docker compose down"
echo "To restart: docker compose up -d"
echo "========================================"
