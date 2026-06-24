<!-- markdownlint-disable MD033 -->
# Sentor Python SDK

**Official Python SDK for the Sentor API — entity-based sentiment analysis, document clustering, and topic naming.**

[![PyPI](https://img.shields.io/pypi/v/sentor-python-sdk?style=flat-square&logo=python&logoColor=white&label=pypi)](https://pypi.org/project/sentor-python-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/sentor-python-sdk?style=flat-square)](https://pypi.org/project/sentor-python-sdk/)
[![License](https://img.shields.io/github/license/NIKX-Tech/sentor-python-sdk?style=flat-square&color=blue)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/NIKX-Tech/sentor-python-sdk?style=flat-square&color=yellow)](https://github.com/NIKX-Tech/sentor-python-sdk/stargazers)
<br>
[![Website](https://img.shields.io/badge/website-sentor.app-5546FA?style=flat-square&logo=google-chrome&logoColor=white)](https://sentor.app)
[![Dashboard](https://img.shields.io/badge/get%20api%20key-dashboard.sentor.app-5546FA?style=flat-square)](https://dashboard.sentor.app/settings?tab=api-access)
[![Docs](https://img.shields.io/badge/docs-sentor.app%2Fdocs-5546FA?style=flat-square)](https://sentor.app/docs)

Stop guessing why ratings drop. Sentor pinpoints exactly how customers feel about specific entities — brands, products, features, competitors — using fine-tuned BERT models trained for aspect-based sentiment analysis.

---

## Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
  - [predict()](#predictdocuments-language)
  - [cluster()](#clusterdocuments-language)
  - [generate_topic_name()](#generate_topic_namecluster_id-documents)
  - [check_health()](#check_health)
- [Error Handling](#-error-handling)
- [Rate Limits](#-rate-limits)
- [Migration from sentor-ml](#-migration-from-sentor-ml)

---

## 📦 Installation

```bash
pip install sentor-python-sdk
```

Get a free API key at [dashboard.sentor.app](https://dashboard.sentor.app/settings?tab=api-access).

---

## 🚀 Quick Start

```python
from sentor import SentorClient

client = SentorClient("your_api_key")

results = client.predict([
    {
        "doc_id": "review-1",
        "doc": "Apple's new iPhone is amazing but the price is ridiculous.",
        "entities": ["Apple", "iPhone", "price"]
    }
])

for item in results["results"]:
    print(item["doc_id"], item["predicted_label"])
    for es in item.get("entity_sentiments", []):
        print(f"  {es['entity']}: {es['sentiment']} ({es['score']:.2f})")
```

---

## 📖 API Reference

### `predict(documents, language="en")`

Score sentiment toward named entities in one or more documents.

```python
results = client.predict(
    documents=[
        {
            "doc_id": "r1",
            "doc": "Samsung's camera is great but battery life is poor.",
            "entities": ["Samsung", "camera", "battery life"]
        }
    ],
    language="en"  # "en" or "nl"
)
```

**Response shape:**

```python
{
    "results": [
        {
            "doc_id": "r1",
            "predicted_class": 0,        # 0=negative, 1=neutral, 2=positive
            "predicted_label": "negative",
            "probabilities": {"negative": 0.72, "neutral": 0.18, "positive": 0.10},
            "details": [...],            # per-sentence breakdown
            "entity_sentiments": [
                {"entity": "Samsung", "sentiment": "neutral", "score": 0.61},
                {"entity": "camera", "sentiment": "positive", "score": 0.88},
                {"entity": "battery life", "sentiment": "negative", "score": 0.91}
            ]
        }
    ]
}
```

**Supported languages:** `en` (English), `nl` (Dutch)

---

### `cluster(documents, language="en")`

Group 5+ documents into thematic clusters using BERTopic + HDBSCAN.

```python
results = client.cluster(
    documents=[
        {"doc_id": "r1", "text": "Shipping was incredibly fast.", "entities": ["shipping"]},
        # ... at least 5 documents
    ],
    language="en"
)

for cluster in results["clusters"]:
    print(cluster["cluster_id"], cluster["document_count"], cluster["top_words"])
# Cluster -1 = outliers that did not fit any topic
```

---

### `generate_topic_name(cluster_id, documents, ...)`

Generate a 3–5 word label for a cluster using an LLM.

```python
result = client.generate_topic_name(
    cluster_id=0,
    documents=cluster["documents"],
    top_words=cluster["top_words"],
    entities=["BrandName"],
    language="en"
)
print(result["topic_name"])  # e.g. "Shipping Delay Complaints"
```

---

### `check_health()`

```python
health = client.check_health()
# {"status": "healthy", "version": "...", "llm_status": "available"}
```

---

## ⚠️ Error Handling

```python
from sentor import SentorClient
from sentor.exceptions import SentorAPIError, RateLimitError, AuthenticationError

client = SentorClient("your_api_key")

try:
    results = client.predict([...])
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit hit. Retry after {e.retry_after}s")
except SentorAPIError as e:
    print(f"API error: {e.message} (code: {e.code})")
```

---

## 📊 Rate Limits

| Plan | Per Minute | Per Day | Per Month |
|------|:---------:|:-------:|:---------:|
| **Free** | 5 | 100 | 1,000 |
| **Starter** | 60 | 1,000 | 10,000 |
| **Growth** | 200 | 3,000 | 30,000 |
| **Business** | 500 | 10,000 | 100,000 |
| **Enterprise** | Custom | Custom | Custom |

[View full pricing →](https://sentor.app/pricing)

---

## 🔄 Migration from `sentor-ml`

This package replaces `sentor-ml`. The import name (`sentor`) and all method signatures are unchanged — only the install command changes:

```bash
pip uninstall sentor-ml
pip install sentor-python-sdk
```

---

## 🔗 Links

- [Sentor Dashboard](https://dashboard.sentor.app) — manage API keys and usage
- [API Documentation](https://sentor.app/docs)
- [PyPI Package](https://pypi.org/project/sentor-python-sdk/)
- [Support](mailto:sentor@nikx.one)

---

<p align="center">
  Built by <a href="https://nikx.one">NIKX Technologies B.V.</a>
</p>
