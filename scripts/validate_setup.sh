#!/bin/bash
# Validation script to check if the setup is correct

set -e

echo "=== Validating crisp_ur_demo setup ==="
echo ""

# Check if Docker is installed
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✓ Docker is installed"

# Check if Docker Compose is installed
echo "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi
echo "✓ Docker Compose is installed"

# Check if .env file exists
echo "Checking environment configuration..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✓ .env file created. Please edit it to configure your robot."
else
    echo "✓ .env file exists"
fi

# Validate required files
echo "Checking required files..."
required_files=(
    "docker/Dockerfile.ur"
    "docker-compose.yaml"
    "crisp_ur_demos/package.xml"
    "crisp_ur_demos/setup.py"
    "crisp_ur_demos/launch/ur.launch.py"
    "crisp_ur_demos/config/ur_controllers.yaml"
    "scripts/setup_middleware.sh"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done
echo "✓ All required files present"

# Validate Python syntax
echo "Validating Python files..."
python3 -m py_compile crisp_ur_demos/setup.py crisp_ur_demos/launch/ur.launch.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Python syntax is valid"
else
    echo "❌ Python syntax errors found"
    exit 1
fi

# Validate YAML syntax
echo "Validating YAML files..."
python3 -c "import yaml; yaml.safe_load(open('crisp_ur_demos/config/ur_controllers.yaml'))"
if [ $? -eq 0 ]; then
    echo "✓ Controllers YAML is valid"
else
    echo "❌ Controllers YAML syntax errors found"
    exit 1
fi

python3 -c "import yaml; yaml.safe_load(open('docker-compose.yaml'))"
if [ $? -eq 0 ]; then
    echo "✓ docker-compose.yaml is valid"
else
    echo "❌ docker-compose.yaml syntax errors found"
    exit 1
fi

# Check X11 access (for RViz)
echo "Checking X11 access..."
if [ -z "$DISPLAY" ]; then
    echo "⚠️  DISPLAY variable not set. RViz may not work."
else
    echo "✓ DISPLAY is set to: $DISPLAY"
fi

echo ""
echo "=== Validation complete! ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file to configure your robot"
echo "2. Build the Docker image: docker compose build"
echo "3. Run the demo: docker compose run --rm launch_ur"
echo ""
