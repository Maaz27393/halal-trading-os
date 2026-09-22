from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class NewsItem(BaseModel):
    contract_version: str = Field(default="1.0.0", description="Canonical contract version")
    source_provider: str = Field(default="news_provider", description="Provider origin identifier")
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of retrieval")
    headline: str = Field(..., description="Article headline")
    summary: str = Field(..., description="Brief summary or abstract")
    url: Optional[str] = Field(default=None, description="Source URL reference")
    symbols: List[str] = Field(default_factory=list, description="Associated ticker symbols")
    sentiment_score: Optional[float] = Field(default=None, description="Sentiment polarity score between -1.0 and 1.0")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
