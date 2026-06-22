import requests
from .exceptions import SentorAPIError, RateLimitError, AuthenticationError
from .models import PredictResponse
from typing import TypedDict, List, Optional


class DocumentInput(TypedDict):
    doc_id: str
    doc: str
    entities: List[str]


class ClusterDocumentInput(TypedDict):
    doc_id: str
    text: str
    entities: List[str]


class TopicDocInput(TypedDict):
    doc_id: str
    text: str
    entities: List[str]
    cluster_probability: float


class SentorClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://sentor.app/api",
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def predict(self, documents: List[DocumentInput], language: str = "en") -> PredictResponse:
        if not documents:
            raise ValueError("Input is required")
        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        response = requests.post(
            f"{self.base_url}/predicts",
            json={"docs": documents},
            headers=self.headers,
            timeout=self.timeout,
            params={"language": language},
        )
        return self._handle_response(response)

    def cluster(
        self,
        documents: List[ClusterDocumentInput],
        language: str = "en",
        n_clusters: Optional[int] = None,
        project_id: Optional[str] = None,
    ):
        if not documents or len(documents) < 5:
            raise ValueError("At least 5 documents are required for clustering")
        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        payload = {"documents": documents}
        if n_clusters is not None:
            payload["n_clusters"] = n_clusters
        if project_id is not None:
            payload["projectId"] = project_id

        response = requests.post(
            f"{self.base_url}/predicts/cluster",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
            params={"language": language},
        )
        return self._handle_response(response)

    def generate_topic_name(
        self,
        cluster_id: int,
        documents: List[TopicDocInput],
        entities: Optional[List[str]] = None,
        top_words: Optional[List[str]] = None,
        language: str = "en",
    ):
        if not documents:
            raise ValueError("At least 1 document is required")
        if language not in ["en", "nl"]:
            raise ValueError("Language must be 'en' or 'nl'")

        response = requests.post(
            f"{self.base_url}/predicts/topic-name",
            json={
                "cluster_id": cluster_id,
                "documents": documents,
                "entities": entities or [],
                "top_words": top_words or [],
            },
            headers=self.headers,
            timeout=self.timeout,
            params={"language": language},
        )
        return self._handle_response(response)

    def check_health(self):
        response = requests.get(
            f"{self.base_url}/predicts/health",
            headers=self.headers,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def _handle_response(self, response):
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 429:
            raise RateLimitError(response.json())
        elif response.status_code == 401:
            raise AuthenticationError(response.json())
        else:
            raise SentorAPIError(response.json())
