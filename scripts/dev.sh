#!/bin/bash
# Development script for Leenkz

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

print_status "Starting Leenkz development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "docker-compose is not available. Please install Docker Compose."
    exit 1
fi

# Use docker compose if available, otherwise docker-compose
COMPOSE_CMD="docker-compose"
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# Function to check if services are healthy
check_services() {
    print_status "Checking service health..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker exec leenkz_postgres_1 pg_isready -U leenkz -d leenkz > /dev/null 2>&1; then
            print_success "PostgreSQL is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "PostgreSQL failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for API
    print_status "Waiting for API..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
            print_success "API is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "API failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Frontend failed to start within 60 seconds"
        exit 1
    fi
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    # Run database initialization
    docker exec leenkz_api_1 uv run python scripts/init_db.py
    
    if [ $? -eq 0 ]; then
        print_success "Database initialized successfully"
    else
        print_error "Database initialization failed"
        exit 1
    fi
}

# Function to show service URLs
show_urls() {
    echo ""
    print_success "Leenkz development environment is ready!"
    echo ""
    echo -e "${GREEN}Services:${NC}"
    echo -e "  ${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "  ${BLUE}API:${NC} http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:8000/api/docs"
    echo -e "  ${BLUE}Database:${NC} localhost:5432 (leenkz/leenkz)"
    echo ""
    echo -e "${GREEN}Useful commands:${NC}"
    echo -e "  ${BLUE}View logs:${NC} $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
    echo -e "  ${BLUE}Stop services:${NC} $COMPOSE_CMD -f docker-compose.dev.yml down"
    echo -e "  ${BLUE}Restart services:${NC} $COMPOSE_CMD -f docker-compose.dev.yml restart"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
}

# Main execution
case "${1:-start}" in
    start)
        print_status "Building and starting services..."
        $COMPOSE_CMD -f docker-compose.dev.yml up --build -d
        
        # Wait for services to be ready
        check_services
        
        # Initialize database
        init_database
        
        # Show URLs
        show_urls
        
        # Follow logs
        $COMPOSE_CMD -f docker-compose.dev.yml logs -f
        ;;
    
    stop)
        print_status "Stopping services..."
        $COMPOSE_CMD -f docker-compose.dev.yml down
        print_success "Services stopped"
        ;;
    
    restart)
        print_status "Restarting services..."
        $COMPOSE_CMD -f docker-compose.dev.yml restart
        print_success "Services restarted"
        ;;
    
    logs)
        $COMPOSE_CMD -f docker-compose.dev.yml logs -f
        ;;
    
    clean)
        print_status "Cleaning up..."
        $COMPOSE_CMD -f docker-compose.dev.yml down -v
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|logs|clean}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the development environment (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Follow service logs"
        echo "  clean   - Stop services and clean up volumes"
        exit 1
        ;;
esac 