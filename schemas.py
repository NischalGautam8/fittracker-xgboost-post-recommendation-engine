from pydantic import BaseModel
from typing import List, Optional

class RecommendRequest(BaseModel):
    userId: str
    limit: Optional[int] = 10

class RankedPost(BaseModel):
    postId: str
    score: float
    reasons: List[str]

class RecommendResponse(BaseModel):
    posts: List[RankedPost]
    modelVersion: str
