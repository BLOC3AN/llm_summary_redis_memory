#!/bin/bash

# Redis Summary Auto-Summary Deployment Script
# Usage: ./deploy.sh [command] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="redis-summary"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check for docker compose (new) or docker-compose (legacy)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        log_error "Docker Compose is not installed"
        exit 1
    fi

    log_success "Requirements check passed (using: $DOCKER_COMPOSE)"
}

setup_env() {
    log_info "Setting up environment..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example $ENV_FILE
            log_warning "Created $ENV_FILE from .env.example"
            log_warning "Please edit $ENV_FILE with your actual API keys"
        else
            log_error ".env.example not found"
            exit 1
        fi
    else
        log_info "$ENV_FILE already exists"
    fi
    
    # Create necessary directories
    mkdir -p logs data
    log_success "Environment setup completed"
}

build_images() {
    log_info "Building Docker images..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    # Prepare build files
    log_info "Preparing build files..."
    ./prepare_build.sh

    $DOCKER_COMPOSE build --no-cache
    log_success "Images built successfully"
}

start_services() {
    local profile=${1:-""}
    log_info "Starting services..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    if [ -n "$profile" ]; then
        $DOCKER_COMPOSE --profile $profile up -d
        log_success "Services started with profile: $profile"
    else
        log_info "No profile specified. Available profiles:"
        log_info "  manual    - Run manual summary execution"
        log_info "  scheduler - Run automatic scheduler"
        log_info "  tools     - Run Redis Commander"
        log_warning "Use: $0 start [profile]"
    fi
}

stop_services() {
    log_info "Stopping services..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE down
    log_success "Services stopped"
}

restart_services() {
    log_info "Restarting services..."
    stop_services
    start_services $1
}

show_status() {
    log_info "Service status:"

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE ps

    log_info "Container logs (last 20 lines):"
    $DOCKER_COMPOSE logs --tail=20
}

show_logs() {
    local service=${1:-""}

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    if [ -n "$service" ]; then
        $DOCKER_COMPOSE logs -f $service
    else
        $DOCKER_COMPOSE logs -f
    fi
}

run_manual_summary() {
    log_info "Running manual summary..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE run --rm redis_summary_app python main.py
}

run_test() {
    log_info "Running tests..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE run --rm redis_summary_app python test_auto_summary.py
}

run_demo() {
    log_info "Running demo..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE run --rm redis_summary_app python demo_auto_summary.py
}

cleanup() {
    log_info "Cleaning up..."

    # Ensure DOCKER_COMPOSE is set
    if [ -z "$DOCKER_COMPOSE" ]; then
        check_requirements
    fi

    $DOCKER_COMPOSE down -v --remove-orphans
    docker system prune -f
    log_success "Cleanup completed"
}

backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    log_info "Creating backup in $backup_dir..."

    mkdir -p $backup_dir

    # Backup logs
    cp -r logs $backup_dir/ 2>/dev/null || true

    # Backup configuration
    cp .env $backup_dir/ 2>/dev/null || true
    cp docker-compose.yml $backup_dir/ 2>/dev/null || true

    log_success "Application backup created in $backup_dir"
    log_info "Note: Redis data is stored on external server (${REDIS_HOST:-192.168.88.165})"
}

show_help() {
    echo "Redis Summary Deployment Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  setup           - Setup environment and check requirements"
    echo "  build           - Build Docker images"
    echo "  start [profile] - Start services (profiles: manual, scheduler, tools)"
    echo "  stop            - Stop all services"
    echo "  restart [profile] - Restart services"
    echo "  status          - Show service status and logs"
    echo "  logs [service]  - Show logs (optionally for specific service)"
    echo "  summary         - Run manual summary"
    echo "  test            - Run tests"
    echo "  demo            - Run demo"
    echo "  backup          - Backup Redis data"
    echo "  cleanup         - Stop services and cleanup"
    echo "  help            - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 setup                    # Initial setup"
    echo "  $0 start                    # Start Redis only"
    echo "  $0 start scheduler          # Start with auto-scheduler"
    echo "  $0 start tools              # Start with Redis Commander"
    echo "  $0 logs redis               # Show Redis logs"
    echo "  $0 summary                  # Run manual summary"
}

# Main script
case "${1:-help}" in
    setup)
        check_requirements
        setup_env
        ;;
    build)
        build_images
        ;;
    start)
        start_services $2
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services $2
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs $2
        ;;
    summary)
        run_manual_summary
        ;;
    test)
        run_test
        ;;
    demo)
        run_demo
        ;;
    backup)
        backup_data
        ;;
    cleanup)
        cleanup
        ;;
    help|*)
        show_help
        ;;
esac
