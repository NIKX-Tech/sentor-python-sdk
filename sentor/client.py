import requests
from .exceptions import SentorAPIError, RateLimitError, AuthenticationError
from typing import TypedDict, List


class DocumentInput(TypedDict):
    """Represents a document to be predicted with its metadata."""

    doc_id: str
    doc: str
    entities: List[str]


class ClusterDocumentInput(TypedDict):
    """Represents a document for clustering."""

    doc_id: str
    text: str
    entities: List[str]


class TopicDocInput(TypedDict):
    """Represents a document for topic naming."""

    doc_id: str
    text: str
    entities: List[str]
    cluster_probability: float


class SentorClient:
    """Client for interacting with the Sentor ML API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://sentor.app/api",
        timeout: int = 30,
    ):
        """
        Initialize the Sentor client with API credentials and configuration.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def predict(self, documents: List[DocumentInput], language: str = "en"):
        """Predict sentiment and entity extraction for documents.

        Args:
            documents: List of documents to predict
            language: Language code for prediction (default: "en").
                Supported languages: "en", "nl"

        Returns:
            dict: Prediction results

        Raises:
            ValueError: If input is empty or invalid language is provided
            RateLimitError: If API rate limit is exceeded
            AuthenticationError: If API key is invalid
            SentorAPIError: For other API errors
        """
        if not documents:
            raise ValueError("Input is required")

        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        url = f"{self.base_url}/predicts"
        params = {"language": language}
        payload = {"docs": documents}
        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            params=params,
        )

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(response.json())
        elif response.status_code == 401:
            raise AuthenticationError(response.json())
        else:
            raise SentorAPIError(response.json())

    def cluster(self, documents: List[ClusterDocumentInput], language: str = "en", n_clusters: int = None, project_id: str = None):
        """Cluster documents using BERTopic.

        Args:
            documents: List of documents to cluster (minimum 5 required)
            language: Language code for prediction (default: "en").
            n_clusters: Optional number of clusters to form.
            project_id: Optional project id.

        Returns:
            dict: Clustering results
        """
        if not documents or len(documents) < 5:
            raise ValueError("At least 5 documents are required for clustering")

        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        url = f"{self.base_url}/predicts/cluster"
        params = {"language": language}
        payload = {"documents": documents}
        if n_clusters is not None:
            payload["n_clusters"] = n_clusters
        if project_id is not None:
            payload["projectId"] = project_id

        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            params=params,
        )

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(response.json())
        elif response.status_code == 401:
            raise AuthenticationError(response.json())
        else:
            raise SentorAPIError(response.json())

    def generate_topic_name(self, cluster_id: int, documents: List[TopicDocInput], entities: List[str] = None, top_words: List[str] = None, language: str = "en"):
        """Generate a descriptive topic name for a cluster using LLM.

        Args:
            cluster_id: ID of the cluster
            documents: List of documents from the cluster
            entities: Optional list of entities to exclude
            top_words: Optional top words from clustering
            language: Language code (default: "en").

        Returns:
            dict: Topic naming results
        """
        if not documents:
            raise ValueError("At least 1 document is required")

        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        url = f"{self.base_url}/predicts/topic-name"
        params = {"language": language}
        payload = {
            "cluster_id": cluster_id,
            "documents": documents,
            "entities": entities or [],
            "top_words": top_words or []
        }

        response = requests.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            params=params,
        )

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(response.json())
        elif response.status_code == 401:
            raise AuthenticationError(response.json())
        else:
            raise SentorAPIError(response.json())

    def check_health(self):
        """Check the health status of the Sentor API.

        Returns:
            dict: Health status information

        Raises:
            SentorAPIError: If health check fails
        """
        url = f"{self.base_url}/predicts/health"
        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise SentorAPIError(response.json())
