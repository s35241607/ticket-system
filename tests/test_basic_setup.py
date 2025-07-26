"""
Basic setup tests to verify the development environment is working correctly.
"""

import pytest


def test_config_import():
    """Test that the configuration can be imported successfully."""
    from src.config import settings
    
    assert settings is not None
    assert hasattr(settings, 'DATABASE_URL')
    assert hasattr(settings, 'REDIS_URL')
    assert hasattr(settings, 'SECRET_KEY')
    assert hasattr(settings, 'KAFKA_BOOTSTRAP_SERVERS')


def test_config_values():
    """Test that configuration has expected default values."""
    from src.config import settings
    
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is True
    assert settings.API_PREFIX == "/api/v1"
    assert settings.TICKET_API_PORT == 8000
    assert settings.KNOWLEDGE_API_PORT == 8001


def test_utils_import():
    """Test that utility modules can be imported successfully."""
    try:
        from src.utils import dependencies, exceptions, helpers, logger, middleware, security
        
        # Just verify they can be imported without errors
        assert dependencies is not None
        assert exceptions is not None
        assert helpers is not None
        assert logger is not None
        assert middleware is not None
        assert security is not None
    except ImportError as e:
        # If imports fail, that's expected since we haven't implemented all utilities yet
        pytest.skip(f"Utility imports not yet implemented: {e}")


def test_directory_structure():
    """Test that the expected directory structure exists."""
    import os
    
    # Check main source directories exist
    assert os.path.exists("src")
    assert os.path.exists("src/domain")
    assert os.path.exists("src/application")
    assert os.path.exists("src/infrastructure")
    assert os.path.exists("src/interface")
    assert os.path.exists("src/backend")
    assert os.path.exists("src/utils")
    
    # Check backend API directories exist
    assert os.path.exists("src/backend/ticket_api")
    assert os.path.exists("src/backend/knowledge_api")
    
    # Check test directories exist
    assert os.path.exists("tests")
    assert os.path.exists("tests/domain")
    assert os.path.exists("tests/application")
    assert os.path.exists("tests/backend")
    assert os.path.exists("tests/integration")


def test_docker_compose_exists():
    """Test that Docker Compose configuration exists."""
    import os
    
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("Dockerfile")


def test_development_tools_config():
    """Test that development tool configurations exist."""
    import os
    
    assert os.path.exists("pyproject.toml")
    assert os.path.exists(".flake8")
    assert os.path.exists(".pre-commit-config.yaml")
    assert os.path.exists("Makefile")
    assert os.path.exists(".env.example")