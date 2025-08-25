"""
Unit tests for Config management.
Tests configuration loading, validation, and error handling.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.utils.config import Config, load_config


class TestConfig:
    """Test cases for Config class and configuration management."""

    @pytest.fixture
    def valid_config_dict(self):
        """Valid configuration dictionary for testing."""
        return {
            "google_cloud_project": "test-project",
            "google_application_credentials": "/tmp/test-credentials.json",
            "bigquery_dataset": "test_dataset",
            "bigquery_table": "test_table",
            "vertex_ai_project": "test-ai-project",
            "vertex_ai_location": "us-central1",
            "vertex_ai_model": "gemini-2.0-flash",
            "log_level": "INFO",
            "environment": "development",
            "max_date_range_days": 30,
            "query_timeout_seconds": 300,
        }

    @pytest.fixture
    def temp_credentials_file(self):
        """Create a temporary credentials file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"type": "service_account", "project_id": "test"}')
            f.flush()
            yield f.name
        # Cleanup
        Path(f.name).unlink(missing_ok=True)

    @pytest.fixture
    def temp_env_file(self, temp_credentials_file):
        """Create a temporary .env file with valid configuration."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash
LOG_LEVEL=INFO
ENVIRONMENT=development
MAX_DATE_RANGE_DAYS=30
QUERY_TIMEOUT_SECONDS=300
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            yield f.name
        # Cleanup
        Path(f.name).unlink(missing_ok=True)

    def test_config_creation_with_all_fields(self, valid_config_dict, temp_credentials_file):
        """Test creating Config with all required fields."""
        config_dict = valid_config_dict.copy()
        config_dict["google_application_credentials"] = temp_credentials_file
        
        config = Config(**config_dict)
        
        assert config.google_cloud_project == "test-project"
        assert config.google_application_credentials == temp_credentials_file
        assert config.bigquery_dataset == "test_dataset"
        assert config.bigquery_table == "test_table"
        assert config.vertex_ai_project == "test-ai-project"
        assert config.vertex_ai_location == "us-central1"
        assert config.vertex_ai_model == "gemini-2.0-flash"
        assert config.log_level == "INFO"
        assert config.environment == "development"
        assert config.max_date_range_days == 30
        assert config.query_timeout_seconds == 300

    def test_config_creation_with_defaults(self, temp_credentials_file):
        """Test creating Config with minimal required fields and defaults."""
        config = Config(
            google_cloud_project="test-project",
            google_application_credentials=temp_credentials_file,
            bigquery_dataset="test_dataset",
            bigquery_table="test_table",
            vertex_ai_project="test-ai-project",
        )
        
        # Check defaults are applied
        assert config.vertex_ai_location == "us-central1"
        assert config.vertex_ai_model == "gemini-2.0-flash"
        assert config.log_level == "INFO"
        assert config.environment == "development"
        assert config.max_date_range_days == 30
        assert config.query_timeout_seconds == 300

    def test_config_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Config()
        
        errors = exc_info.value.errors()
        required_fields = {
            "google_cloud_project",
            "google_application_credentials",
            "bigquery_dataset",
            "bigquery_table",
            "vertex_ai_project",
        }
        
        error_fields = {error["loc"][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_config_invalid_types(self, temp_credentials_file):
        """Test that invalid types raise ValidationError."""
        with pytest.raises(ValidationError):
            Config(
                google_cloud_project="test-project",
                google_application_credentials=temp_credentials_file,
                bigquery_dataset="test_dataset",
                bigquery_table="test_table",
                vertex_ai_project="test-ai-project",
                max_date_range_days="not_an_integer",  # Invalid type
            )
        
        with pytest.raises(ValidationError):
            Config(
                google_cloud_project="test-project",
                google_application_credentials=temp_credentials_file,
                bigquery_dataset="test_dataset",
                bigquery_table="test_table",
                vertex_ai_project="test-ai-project",
                query_timeout_seconds="not_an_integer",  # Invalid type
            )

    def test_load_config_with_valid_env_file(self, temp_env_file):
        """Test loading configuration from a valid .env file."""
        config = load_config(temp_env_file)
        
        assert isinstance(config, Config)
        assert config.google_cloud_project == "test-project"
        assert config.bigquery_dataset == "test_dataset"
        assert config.bigquery_table == "test_table"
        assert config.vertex_ai_project == "test-ai-project"

    def test_load_config_file_not_found(self):
        """Test that FileNotFoundError is raised for missing config file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            load_config("/nonexistent/path/.env")

    def test_load_config_credentials_file_not_found(self):
        """Test that FileNotFoundError is raised for missing credentials file."""
        env_content = """
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS=/nonexistent/credentials.json
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                with pytest.raises(FileNotFoundError, match="Service account file not found"):
                    load_config(f.name)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_load_config_with_current_directory_default(self, temp_credentials_file):
        """Test loading config from current directory when no path specified."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
        """.strip()
        
        # Create .env in current directory
        current_env = Path.cwd() / ".env"
        current_env.write_text(env_content)
        
        try:
            config = load_config()
            assert config.google_cloud_project == "test-project"
        finally:
            current_env.unlink(missing_ok=True)

    def test_load_config_environment_variable_types(self, temp_credentials_file):
        """Test that environment variables are properly converted to correct types."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
MAX_DATE_RANGE_DAYS=45
QUERY_TIMEOUT_SECONDS=600
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = load_config(f.name)
                assert isinstance(config.max_date_range_days, int)
                assert config.max_date_range_days == 45
                assert isinstance(config.query_timeout_seconds, int)
                assert config.query_timeout_seconds == 600
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_load_config_invalid_integer_values(self, temp_credentials_file):
        """Test that invalid integer environment variables raise ValueError."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
MAX_DATE_RANGE_DAYS=not_an_integer
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                with pytest.raises(ValueError):
                    load_config(f.name)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_load_config_with_environment_overrides(self, temp_env_file):
        """Test that existing environment variables override .env file values."""
        # Set environment variable that should override .env file
        with patch.dict(os.environ, {"VERTEX_AI_MODEL": "custom-model"}):
            config = load_config(temp_env_file)
            assert config.vertex_ai_model == "custom-model"

    def test_load_config_missing_required_env_vars(self, temp_credentials_file):
        """Test that missing required environment variables raise ValidationError."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
# Missing BIGQUERY_DATASET
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                with pytest.raises(ValidationError):
                    load_config(f.name)
            finally:
                Path(f.name).unlink(missing_ok=True)

    def test_config_serialization(self, valid_config_dict, temp_credentials_file):
        """Test that Config can be serialized/deserialized."""
        config_dict = valid_config_dict.copy()
        config_dict["google_application_credentials"] = temp_credentials_file
        
        config = Config(**config_dict)
        
        # Test dict representation
        config_dict_output = config.model_dump()
        assert isinstance(config_dict_output, dict)
        assert config_dict_output["google_cloud_project"] == "test-project"
        
        # Test JSON representation
        config_json = config.model_dump_json()
        assert isinstance(config_json, str)
        assert "test-project" in config_json

    def test_config_immutability(self, valid_config_dict, temp_credentials_file):
        """Test that Config objects are properly typed and validated."""
        config_dict = valid_config_dict.copy()
        config_dict["google_application_credentials"] = temp_credentials_file
        
        config = Config(**config_dict)
        
        # All fields should be accessible
        assert hasattr(config, "google_cloud_project")
        assert hasattr(config, "vertex_ai_model")
        assert hasattr(config, "max_date_range_days")

    def test_credentials_path_validation(self):
        """Test that credentials file path validation works correctly."""
        with pytest.raises(FileNotFoundError, match="Service account file not found"):
            load_config_dict = {
                "GOOGLE_CLOUD_PROJECT": "test-project",
                "GOOGLE_APPLICATION_CREDENTIALS": "/nonexistent/file.json",
                "BIGQUERY_DATASET": "test_dataset", 
                "BIGQUERY_TABLE": "test_table",
                "VERTEX_AI_PROJECT": "test-ai-project",
            }
            
            env_content = "\n".join(f"{k}={v}" for k, v in load_config_dict.items())
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
                f.write(env_content)
                f.flush()
                
                try:
                    load_config(f.name)
                finally:
                    Path(f.name).unlink(missing_ok=True)

    def test_path_object_handling(self, temp_credentials_file):
        """Test that Path objects are handled correctly in config loading."""
        env_content = f"""
GOOGLE_CLOUD_PROJECT=test-project
GOOGLE_APPLICATION_CREDENTIALS={temp_credentials_file}
BIGQUERY_DATASET=test_dataset
BIGQUERY_TABLE=test_table
VERTEX_AI_PROJECT=test-ai-project
        """.strip()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                # Test with Path object
                config = load_config(Path(f.name))
                assert config.google_cloud_project == "test-project"
            finally:
                Path(f.name).unlink(missing_ok=True)