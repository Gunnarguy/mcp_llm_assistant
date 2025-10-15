# Testing Guide

## Running Tests

### Quick Start

```bash
# Run all tests
./run_tests.sh

# Or manually
pytest tests/ -v
```

### Test Coverage

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_docker_service.py -v

# Run specific test
pytest tests/test_api.py::TestAPIEndpoints::test_root_endpoint -v

# Run tests with keyword
pytest tests/ -k "docker" -v
```

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_docker_service.py  # Docker service tests
├── test_api.py          # API endpoint tests
└── test_exceptions.py   # Exception handling tests
```

## Writing New Tests

### Example Test

```python
import pytest
from app.services.docker_service import DockerService

def test_docker_service_health(docker_service_mock):
    """Test Docker service health check."""
    service = docker_service_mock
    assert service.is_healthy() is True
```

### Using Fixtures

```python
def test_with_sample_data(sample_chat_request):
    """Test using shared fixture."""
    assert sample_chat_request["prompt"] == "What containers are running?"
```

## Test Coverage Goals

- **Services:** 80%+ coverage
- **API Endpoints:** 90%+ coverage
- **Exceptions:** 100% coverage

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=app --cov-report=xml
```
