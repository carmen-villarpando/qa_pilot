"""Configuration for user's custom GEval metrics.

This module reads metrics configuration from utils/metrics.py as text to avoid
instantiating GEval objects. The system only analyzes the metrics to determine
which ones to use, it does not execute them.
"""

import re
from typing import Dict, List
from pathlib import Path

# Path to utils/metrics.py
METRICS_FILE = Path(__file__).parent.parent / "utils" / "metrics.py"

# Cache for parsed metrics
_CACHED_METRICS = None


def _parse_metrics_file() -> Dict:
    """Parse utils/metrics.py to extract metric configurations without instantiating GEval objects."""
    global _CACHED_METRICS
    if _CACHED_METRICS is not None:
        return _CACHED_METRICS
    
    if not METRICS_FILE.exists():
        print(f"Warning: Metrics file not found at {METRICS_FILE}")
        return {}
    
    with open(METRICS_FILE, 'r') as f:
        content = f.read()
    
    metrics = {}
    
    # Find all metric definitions (pattern: variable_name = GEval(...))
    metric_pattern = r'(\w+_metric)\s*=\s*GEval\('
    
    for match in re.finditer(metric_pattern, content):
        metric_name = match.group(1)
        
        # Find the closing parenthesis for this GEval call
        start_pos = match.end()
        bracket_count = 1
        end_pos = start_pos
        
        while end_pos < len(content) and bracket_count > 0:
            if content[end_pos] == '(':
                bracket_count += 1
            elif content[end_pos] == ')':
                bracket_count -= 1
            end_pos += 1
        
        metric_content = content[start_pos:end_pos - 1]
        
        # Extract name
        name_match = re.search(r'name\s*=\s*"([^"]+)"', metric_content)
        name = name_match.group(1) if name_match else metric_name
        
        # Extract evaluation_steps
        steps_match = re.search(r'evaluation_steps\s*=\s*\[(.*?)\]', metric_content, re.DOTALL)
        evaluation_steps = []
        if steps_match:
            steps_content = steps_match.group(1)
            # Extract all quoted strings
            step_matches = re.findall(r'"([^"]+)"', steps_content)
            evaluation_steps = step_matches
        
        # Extract threshold
        threshold_match = re.search(r'threshold\s*=\s*([\d.]+)', metric_content)
        threshold = float(threshold_match.group(1)) if threshold_match else 0.8
        
        # Extract evaluation_params
        params = []
        if 'LLMTestCaseParams.ACTUAL_OUTPUT' in metric_content:
            params.append("ACTUAL_OUTPUT")
        if 'LLMTestCaseParams.EXPECTED_OUTPUT' in metric_content:
            params.append("EXPECTED_OUTPUT")
        
        metrics[metric_name] = {
            "name": name,
            "evaluation_steps": evaluation_steps,
            "threshold": threshold,
            "evaluation_params": params
        }
    
    _CACHED_METRICS = metrics
    return metrics


def get_metrics_config() -> Dict:
    """Get all metrics configuration from utils/metrics.py."""
    return _parse_metrics_file()


# Context keywords for each metric (for intelligent selection)
CONTEXT_KEYWORDS = {
    "pii_leakage_metric": ["personal", "data", "private", "sensitive", "customer", "account", "information", "identity"],
    "bias_metric": ["bias", "fairness", "discrimination", "stereotype", "diversity", "inclusive"],
    "diversity_metric": ["diverse", "background", "inclusive", "variety", "different", "culture"],
    "ethical_alignment_metric": ["ethical", "moral", "harmful", "dangerous", "illegal", "responsibility"],
    "professionalism_metric": ["professional", "expertise", "formal", "business", "corporate"],
    "empathy_metric": ["empathy", "understanding", "compassion", "care", "support", "emotional"],
    "directness_metric": ["direct", "clear", "concise", "straightforward", "efficient"],
    "clarity_metric": ["clear", "understandable", "simple", "explanation", "confusing"],
    "fluency_metric": ["grammar", "spelling", "language", "writing", "fluency"],
    "consistency_metric": ["consistent", "style", "tone", "terminology", "contradiction"],
    "conciseness_metric": ["concise", "brief", "short", "verbose", "redundant"],
    "repetitiveness_metric": ["repetitive", "redundant", "repeat", "duplicate"],
    "grammar_spelling_metric": ["grammar", "spelling", "punctuation", "writing", "english"],
    "correctness_metric": ["correct", "accurate", "financial", "illegal", "fraudulent", "compliance", "policy"],
    "compliance_metric": ["compliance", "policy", "becu", "regulation", "financial", "offering"]
}


def get_relevant_metrics(issue_title: str, issue_body: str = "") -> List[str]:
    """Get relevant metrics based on issue context."""
    metrics_config = get_metrics_config()
    text = f"{issue_title} {issue_body}".lower()
    
    relevant_metrics = []
    
    # Always include core metrics for financial chatbot
    core_metrics = ["correctness_metric", "compliance_metric", "pii_leakage_metric"]
    for metric_name in core_metrics:
        if metric_name in metrics_config:
            relevant_metrics.append(metric_name)
    
    # Add context-specific metrics based on keywords
    for metric_name, keywords in CONTEXT_KEYWORDS.items():
        if metric_name in relevant_metrics:
            continue  # Skip already added core metrics
        
        for keyword in keywords:
            if keyword in text:
                relevant_metrics.append(metric_name)
                break  # Add metric once if any keyword matches
    
    # Add quality metrics for conversational AI
    quality_metrics = ["professionalism_metric", "empathy_metric", "clarity_metric"]
    for metric_name in quality_metrics:
        if metric_name in metrics_config and metric_name not in relevant_metrics:
            relevant_metrics.append(metric_name)
    
    return relevant_metrics


def get_metric_config(metric_name: str) -> Dict:
    """Get configuration for a specific metric from utils/metrics.py."""
    metrics_config = get_metrics_config()
    return metrics_config.get(metric_name, {})


def get_all_metric_names() -> List[str]:
    """Get all available custom metric names."""
    metrics_config = get_metrics_config()
    return list(metrics_config.keys())
