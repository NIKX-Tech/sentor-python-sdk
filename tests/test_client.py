import pytest
from sentor import SentorClient
from sentor.exceptions import (
    SentorAPIError,
    RateLimitError,
    AuthenticationError,
)
from unittest.mock import Mock, patch


@pytest.fixture
def mock_client():
    """Create a mock SentorClient instance for testing."""
    client = SentorClient("test-key")
    return client


def test_client_initialization():
    """Test proper initialization of SentorClient with default parameters."""
    client = SentorClient(api_key="test-key")
    assert isinstance(client, SentorClient)
    assert client.api_key == "test-key"
    assert client.base_url == "https://sentor.app/api"
    assert client.timeout == 30


@patch("requests.post")
def test_predict_success(mock_post):
    """Test successful document prediction with positive sentiment."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "predicted_label": "positive",
                "probabilities": {"positive": 0.95},
            }
        ]
    }
    mock_post.return_value = mock_response

    # Test the predict method
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]
    result = client.predict(documents)

    assert result["results"][0]["predicted_label"] == "positive"
    assert result["results"][0]["probabilities"]["positive"] == 0.95
    mock_post.assert_called_once()

    # Verify the language parameter was passed correctly
    call_args = mock_post.call_args
    assert call_args[1]["params"] == {"language": "en"}


@patch("requests.post")
def test_predict_rate_limit(mock_post):
    """Test rate limit error handling during document prediction."""
    # Setup mock response for rate limit error
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.json.return_value = {
        "detail": "Rate limit exceeded",
        "retry_after": 60,
    }
    mock_post.return_value = mock_response

    # Test rate limit error
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]

    with pytest.raises(RateLimitError) as exc_info:
        client.predict(documents)

    assert exc_info.value.retry_after == 60


@patch("requests.post")
def test_predict_auth_error(mock_post):
    """Test authentication error handling during document prediction."""
    # Setup mock response for authentication error
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid API key"}
    mock_post.return_value = mock_response

    # Test authentication error
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]

    with pytest.raises(AuthenticationError):
        client.predict(documents)


def test_predict_empty_input():
    """Test validation of empty input in document prediction."""
    client = SentorClient("test-key")
    with pytest.raises(ValueError, match="Input is required"):
        client.predict([])


@patch("requests.post")
def test_predict_with_dutch_language(mock_post):
    """Test document prediction with Dutch language parameter."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "predicted_label": "positive",
                "probabilities": {"positive": 0.95},
            }
        ]
    }
    mock_post.return_value = mock_response

    # Test the predict method with Dutch language
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]
    result = client.predict(documents, language="nl")

    assert result["results"][0]["predicted_label"] == "positive"

    # Verify the language parameter was passed correctly
    call_args = mock_post.call_args
    assert call_args[1]["params"] == {"language": "nl"}


def test_predict_invalid_language():
    """Test validation of invalid language parameter."""
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]

    with pytest.raises(ValueError, match="Language must be 'en' or 'nl'"):
        client.predict(documents, language="invalid")


def test_predict_explicit_english_language():
    """Test document prediction with explicit English language parameter."""
    client = SentorClient("test-key")
    documents = [{"doc_id": "1", "doc": "Test text", "entities": []}]

    # This should not raise an error
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_post.return_value = mock_response

        client.predict(documents, language="en")

        # Verify the language parameter was passed correctly
        call_args = mock_post.call_args
        assert call_args[1]["params"] == {"language": "en"}


@patch("requests.get")
def test_check_health_success(mock_get):
    """Test successful health check response."""
    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}
    mock_get.return_value = mock_response

    # Test health check
    client = SentorClient("test-key")
    result = client.check_health()

    assert result["status"] == "healthy"
    mock_get.assert_called_once()


@patch("requests.get")
def test_check_health_error(mock_get):
    """Test error handling during health check."""
    # Setup mock response for error
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Internal server error"}
    mock_get.return_value = mock_response

    # Test health check error
    client = SentorClient("test-key")
    with pytest.raises(SentorAPIError):
        client.check_health()


if __name__ == "__main__":
    pytest.main([__file__])
