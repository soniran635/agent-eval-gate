from pydantic import BaseModel, Field
from typing import List, Optional

class EvalTestCase(BaseModel):
    test_id: str
    category: str
    prompt: str
    expected_keys: List[str] = []
    rubric: str

class EvalResult(BaseModel):
    test_id: str
    category: str
    passed: bool
    score: float  # 0.0 to 1.0
    latency_sec: float
    model_response: str
    judge_reasoning: str

class ReleaseGateSummary(BaseModel):
    total_tests: int
    passed_tests: int
    overall_accuracy: float
    avg_latency_sec: float
    hallucination_rate: float
    release_verdict: str  # 'APPROVED' or 'BLOCKED'
    blocking_reasons: List[str] = []
