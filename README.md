# Leenkz - Link Keeper

Keep your links tagged and stored available on any device.

## Features

- **🔗 Link Management**: Add, edit, and delete links with titles and descriptions
- **🏷️ Tagging System**: Organize links with custom tags and colors
- **📸 Snapshots**: Capture and store link content with compression support
- **👁️ In-Browser Viewing**: Render snapshots directly in the browser
- **🔄 Content Deduplication**: Prevent storing identical snapshots using SHA-256 hashing
- **🤝 Sharing**: Share links with other users with custom messages
- **👑 Admin Panel**: User management and system administration
- **🔐 Authentication**: Secure JWT-based user authentication
- **📱 Modern UI**: React frontend with shadcn/ui components
- **🚀 RESTful API**: Complete API with OpenAPI documentation

## Quick Start

### Option 1: Docker Development (Recommended)

The easiest way to get started is using Docker with hot reloading:

```bash
# Clone the repository
git clone https://github.com/leenkz/leenkz.git
cd leenkz

# Start the development environment
./scripts/dev.sh

# Or manually with Docker Compose
docker-compose -f docker-compose.dev.yml up --build
```

This will start:
- **Frontend**: http://localhost:3000 (React with hot reload)
- **API**: http://localhost:8000 (FastAPI with auto-reload)
- **Database**: PostgreSQL on localhost:5432
- **API Docs**: http://localhost:8000/api/docs

### Option 2: Local Development

#### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- PostgreSQL 12+
- uv (recommended) or pip

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/leenkz/leenkz.git
   cd leenkz
   ```

2. **Install Python dependencies**
   ```bash
   uv pip install -e .
   # Or with compression support:
   uv pip install -e ".[compression]"
   ```

3. **Install frontend dependencies**
   ```bash
   npm install
   ```

4. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env with your database and other settings
   ```

5. **Initialize database**
   ```bash
   ./scripts/init_db.sh
   ```

6. **Start development server**
   ```bash
   uv run leenkz dev
   ```

The application will be available at:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Development Commands

### Docker Development

```bash
# Start development environment
./scripts/dev.sh

# Stop all services
./scripts/dev.sh stop

# Restart services
./scripts/dev.sh restart

# View logs
./scripts/dev.sh logs

# Clean up (removes volumes)
./scripts/dev.sh clean
```

### Local Development

```bash
# Start API with hot reload
uv run leenkz dev

# Start frontend with hot reload
npm run dev

# Run tests
uv run pytest

# Run linting
uv run leenkz lint

# Database migrations
uv run leenkz migrate

# Seed database
uv run leenkz seed
```

## Link Snapshots

Leenkz includes a powerful snapshot feature that allows you to capture and store the content of your links:

### Features

- **Content Capture**: Fetch content from HTTP/HTTPS URLs
- **Compression Support**: Gzip and Zstandard compression algorithms
- **MIME Type Detection**: Automatic content type detection
- **Size Limits**: Configurable maximum file size (default: 25MB)
- **Security**: MIME type filtering for security
- **Metadata Storage**: Store ETags, last-modified dates, and checksums
- **In-Browser Viewing**: Render snapshots directly in the browser
- **Content Deduplication**: Prevent storing identical snapshots using SHA-256 hashing

### API Endpoints

- `POST /api/links/{link_id}/snapshot` - Create a new snapshot
- `GET /api/links/{link_id}/snapshots` - List all snapshots for a link
- `GET /api/snapshots/{snapshot_id}` - Get snapshot metadata
- `GET /api/snapshots/{snapshot_id}/raw` - Download raw snapshot content
- `GET /api/snapshots/{snapshot_id}/render` - Get content for in-browser rendering
- `DELETE /api/snapshots/{snapshot_id}` - Delete a snapshot

### Configuration

```bash
# Maximum snapshot size in MB
SNAPSHOT_MAX_SIZE_MB=25

# Allowed MIME types (regex pattern)
SNAPSHOT_ALLOWED_MIME_REGEX=.*
```

### Compression Options

- **None**: Store content without compression
- **Gzip**: Standard compression (good compression ratio)
- **Zstandard**: Modern compression (better ratio, faster)

### Snapshot Deduplication

Leenkz automatically prevents storing duplicate snapshots by comparing SHA-256 content hashes:

#### How It Works

1. **Content Hashing**: Each snapshot's raw content is hashed using SHA-256
2. **Duplicate Detection**: Before creating a new snapshot, the system checks for existing snapshots with the same content hash
3. **Smart Response**: 
   - **201 Created**: New snapshot created
   - **208 Already Reported**: Identical content found, returns existing snapshot
   - **Force Override**: Use `force=true` parameter to bypass deduplication

#### API Contract

```bash
# Normal snapshot creation (with deduplication)
curl -X POST "http://localhost:8000/api/links/1/snapshot" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"compression": "gzip"}'

# Force creation (bypass deduplication)
curl -X POST "http://localhost:8000/api/links/1/snapshot" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"compression": "gzip", "force": true}'
```

#### Response Codes

- **201 Created**: New snapshot created successfully
- **208 Already Reported**: Identical content found, existing snapshot returned
- **422 Validation Error**: Invalid parameters or content
- **400 Bad Request**: Content too large or MIME type not allowed

#### Frontend Integration

The React frontend automatically handles deduplication responses:

- **Success Toast**: Shows compression info and size for new snapshots
- **Deduplication Toast**: Shows hash prefix when identical content is detected
- **Hash Display**: Snapshot table shows first 8 characters of content hash
- **Force Toggle**: Optional UI control to bypass deduplication

#### Database Schema

```sql
-- Content hash column for deduplication
ALTER TABLE link_snapshots ADD COLUMN content_hash CHAR(64);

-- Unique composite index for efficient lookups
CREATE UNIQUE INDEX ux_link_snapshots_link_id_hash 
    ON link_snapshots (link_id, content_hash);

-- Performance index on content_hash
CREATE INDEX ix_link_snapshots_content_hash 
    ON link_snapshots (content_hash);
```

### Usage Example

```bash
# Create a snapshot with gzip compression
curl -X POST "http://localhost:8000/api/links/1/snapshot" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"compression": "gzip"}'

# Download snapshot content
curl "http://localhost:8000/api/snapshots/1/raw" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get snapshot for in-browser rendering
curl "http://localhost:8000/api/snapshots/1/render" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### In-Browser Viewing

The snapshot system supports in-browser rendering for browser-friendly content types:

- **HTML**: Rendered in an iframe with DOMPurify sanitization
- **Markdown**: Rendered with React Markdown
- **Images**: Displayed directly with proper sizing
- **Text/Code**: Syntax-highlighted in a pre-formatted block
- **JSON/XML**: Formatted and syntax-highlighted

Non-renderable content types automatically trigger a download instead.

## Architecture

### Backend

- **FastAPI**: Modern Python web framework
- **SQLModel**: SQL database toolkit and ORM
- **PostgreSQL**: Primary database
- **Alembic**: Database migrations
- **JWT**: Authentication
- **Pydantic**: Data validation

### Frontend

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **shadcn/ui**: Component library
- **React Query**: Data fetching
- **React Router**: Navigation
- **React Markdown**: Markdown rendering
- **DOMPurify**: HTML sanitization

### Development Tools

- **uv**: Python package manager
- **npm**: Node.js package manager
- **Docker**: Containerization
- **Ruff**: Python linter
- **Black**: Code formatter
- **MyPy**: Type checker
- **Pre-commit**: Git hooks

## Development

### Running Tests

```bash
# Python tests
uv run pytest

# Frontend tests
npm test
```

### Code Quality

```bash
# Format code
uv run black .
uv run ruff --fix .

# Type checking
uv run mypy .

# Lint frontend
npm run lint
```

### Database Migrations

```bash
# Create migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head
```

## Deployment

### Docker

```bash
# Build image
docker build -t leenkz .

# Run with Docker Compose
docker-compose up -d
```

### Environment Variables

See `env.example` for all available configuration options.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [shadcn/ui](https://ui.shadcn.com/) for the beautiful component library
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
