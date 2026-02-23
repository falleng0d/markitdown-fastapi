# MarkItDown FastAPI

A FastAPI application that converts web pages to clean, formatted markdown using [MarkItDown](https://github.com/microsoft/markitdown) and [OpenAI](https://openai.com/) for text cleanup.

## Features

- Convert any web page URL to clean markdown
- AI-powered text cleanup and formatting using OpenAI
- Automatic content type detection (articles, job descriptions, etc.)
- RESTful API with OpenAPI documentation

## Requirements

- Python 3.14+
- OpenAI API key (or compatible API)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd markitdown

# Install dependencies using uv
uv sync
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
DEBUG=false
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: use a different API endpoint
DEFAULT_MODEL=gpt-4o                         # Optional: specify default model
```

## Usage

### Running the Server

```bash
uv run fastapi dev app/__main__.py
```

The API will be available at `http://localhost:8000`.

### API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### POST /v1/convert

Converts a web page URL to cleaned markdown.

**Request Body:**
```json
{
  "uri": "https://example.com/article",
  "model": "gpt-4o"
}
```

| Parameter | Type   | Required | Description                          |
|-----------|--------|----------|--------------------------------------|
| uri       | string | Yes      | The URL of the web page to convert   |
| model     | string | No       | OpenAI model to use (default: gpt-4o)|

**Response:**
Returns the cleaned markdown content as plain text.

**Example:**
```bash
curl -X POST http://localhost:8000/v1/convert \
  -H "Content-Type: application/json" \
  -d '{"uri": "https://openai.com"}'
```

## How It Works

1. The application fetches the web page content using MarkItDown
2. MarkItDown extracts and converts the content to raw markdown
3. The raw markdown is sent to OpenAI for cleanup and formatting
4. The cleaned markdown is returned to the client

## Development

### Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting with a line length of 127 characters.

```bash
# Run linter
uv run ruff check app/

# Format code
uv run ruff format app/
```

## License

MIT
