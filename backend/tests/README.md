# Backend Testing Guide

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_appointment_service.py
│   ├── test_auth_service.py
│   └── ...
├── api/                     # API integration tests
│   ├── test_appointments_api.py
│   ├── test_auth_api.py
│   └── ...
└── integration/             # Integration tests
    └── ...
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_appointment_service.py

# Run specific test
pytest tests/unit/test_appointment_service.py::test_book_appointment_success

# Run by marker
pytest -m unit
pytest -m api
```

## Test Categories

### Unit Tests
- Test individual functions/classes in isolation
- Mock external dependencies
- Fast execution
- Located in `tests/unit/`

### API Tests
- Test HTTP endpoints
- Test authentication/authorization
- Test request/response cycles
- Located in `tests/api/`

### Integration Tests
- Test multiple components together
- Use test database
- Test complete workflows
- Located in `tests/integration/`

## Fixtures

Common fixtures in `conftest.py`:
- `db_session`: Test database session
- `client`: FastAPI test client
- `sample_user_data`: Sample user data
- `sample_patient_data`: Sample patient data

## Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies in unit tests
3. **Fixtures**: Use fixtures for common setup
4. **Naming**: Use descriptive test names
5. **Assertions**: Use specific assertions
6. **Coverage**: Aim for >80% code coverage
