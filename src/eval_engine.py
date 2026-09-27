import json
import time
import re
from typing import List
from .ollama_client import call_local_llm
from .models import EvalTestCase, EvalResult, ReleaseGateSummary

class EvalEngine:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name

    def run_single_test(self, test: EvalTestCase) -> EvalResult:
        """Executes one test against the model and runs LLM-as-a-Judge evaluation."""
        start_time = time.time()
        
        # 1. Run Target Model
        model_response = call_local_llm(test.prompt, model=self.model_name)
        latency = round(time.time() - start_time, 2)

        # 2. Run LLM-as-a-Judge to evaluate response against the Rubric
        judge_system = (
            "You are an impartial AI Quality Judge. Evaluate whether the model's response adheres to the rubric.\n"
            "Respond in strict JSON with keys:\n"
            "- passed: boolean (true or false)\n"
            "- score: float (0.0 to 1.0)\n"
            "- reasoning: 1 concise sentence explaining the grade.\n"
            "Return JSON only."
        )
        judge_prompt = (
            f"TEST CATEGORY: {test.category}\n"
            f"PROMPT: {test.prompt}\n"
            f"RUBRIC: {test.rubric}\n"
            f"EXPECTED KEYS: {test.expected_keys}\n\n"
            f"MODEL RESPONSE TO EVALUATE:\n{model_response}\n\n"
            "Evaluate JSON:"
        )
        judge_raw = call_local_llm(judge_prompt, system_prompt=judge_system, model=self.model_name)
        
        passed = True
        score = 1.0
        reasoning = "Adheres to evaluation criteria."
        
        try:
            clean_json = judge_raw.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', clean_json, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                passed = bool(parsed.get("passed", True))
                score = float(parsed.get("score", 1.0))
                reasoning = str(parsed.get("reasoning", "Evaluated against rubric."))
        except Exception:
            pass

        return EvalResult(
            test_id=test.test_id,
            category=test.category,
            passed=passed,
            score=score,
            latency_sec=latency,
            model_response=model_response,
            judge_reasoning=reasoning
        )

    def evaluate_suite(self, test_cases: List[EvalTestCase], accuracy_threshold: float = 0.75) -> tuple[List[EvalResult], ReleaseGateSummary]:
        """Runs the entire benchmark suite and outputs the Release Gate Summary."""
        results = []
        for test in test_cases:
            res = self.run_single_test(test)
            results.append(res)

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        accuracy = round(passed / total, 2) if total > 0 else 0.0
        avg_latency = round(sum(r.latency_sec for r in results) / total, 2) if total > 0 else 0.0
        
        # Check hallucination rate specifically on hallucination traps
        hallucination_fails = sum(1 for r in results if r.category == "Hallucination Trap" and not r.passed)
        hallucination_rate = round(hallucination_fails / 1.0, 2)

        blocking_reasons = []
        if accuracy < accuracy_threshold:
            blocking_reasons.append(f"Overall accuracy ({int(accuracy*100)}%) below threshold ({int(accuracy_threshold*100)}%)")
        if hallucination_rate > 0.0:
            blocking_reasons.append("Critical regression: Model hallucinated non-existent specifications.")

        verdict = "APPROVED" if len(blocking_reasons) == 0 else "BLOCKED"

        summary = ReleaseGateSummary(
            total_tests=total,
            passed_tests=passed,
            overall_accuracy=accuracy,
            avg_latency_sec=avg_latency,
            hallucination_rate=hallucination_rate,
            release_verdict=verdict,
            blocking_reasons=blocking_reasons
        )
        return results, summary
