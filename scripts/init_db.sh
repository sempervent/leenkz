#!/bin/bash
# Database initialization script wrapper

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

print_status "Starting database initialization..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if uv is available (preferred)
if command -v uv &> /dev/null; then
    print_status "Using uv for Python environment"
    PYTHON_CMD="uv run python"
else
    print_warning "uv not found, using system Python"
    PYTHON_CMD="python3"
fi

# Check if .env file exists
if [ -f ".env" ]; then
    print_status "Loading environment from .env file"
    export $(grep -v '^#' .env | xargs)
else
    print_warning "No .env file found, using system environment variables"
fi

# Set default values if not provided
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://leenkz:leenkz@localhost/leenkz}"
export SEED_DATABASE="${SEED_DATABASE:-false}"

print_status "Database URL: $DATABASE_URL"
print_status "Seed database: $SEED_DATABASE"

# Run the Python initialization script
print_status "Running database initialization..."
$PYTHON_CMD scripts/init_db.py

if [ $? -eq 0 ]; then
    print_success "Database initialization completed successfully!"
else
    print_error "Database initialization failed!"
    exit 1
fi 