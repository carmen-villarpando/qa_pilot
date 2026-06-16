"""Configuration for user's custom GEval metrics.

This module loads metrics from utils/metrics.py to avoid duplication.
"""

import sys
import os
from typing import Dict, List
from pathlib import Path

# Add utils directory to path to import metrics
utils_path = Path(__file__).parent.parent / "utils"
sys.path.insert(0, str(utils_path))

try:
    from metrics import (
        pii_leakage_metric,
        bias_metric,
        diversity_metric,
        ethical_alignment_metric,
        professionalism_metric,
        empathy_metric,
        directness_metric,
        clarity_metric,
        fluency_metric,
        consistency_metric,
        conciseness_metric,
        repetitiveness_metric,
        grammar_spelling_metric,
        correctness_metric,
        compliance_metric
    )
    
    # Map metric objects to their configuration
    METRIC_OBJECTS = {
        "pii_leakage_metric": pii_leakage_metric,
        "bias_metric": bias_metric,
        "diversity_metric": diversity_metric,
        "ethical_alignment_metric": ethical_alignment_metric,
        "professionalism_metric": professionalism_metric,
        "empathy_metric": empathy_metric,
        "directness_metric": directness_metric,
        "clarity_metric": clarity_metric,
        "fluency_metric": fluency_metric,
        "consistency_metric": consistency_metric,
        "conciseness_metric": conciseness_metric,
        "repetitiveness_metric": repetitiveness_metric,
        "grammar_spelling_metric": grammar_spelling_metric,
        "correctness_metric": correctness_metric,
        "compliance_metric": compliance_metric
    }
except ImportError:
    METRIC_OBJECTS = {}
    print("Warning: Could not import metrics from utils/metrics.py")

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
    text = f"{issue_title} {issue_body}".lower()
    
    relevant_metrics = []
    
    # Always include core metrics for financial chatbot
    core_metrics = ["correctness_metric", "compliance_metric", "pii_leakage_metric"]
    for metric_name in core_metrics:
        if metric_name in METRIC_OBJECTS:
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
        if metric_name in METRIC_OBJECTS and metric_name not in relevant_metrics:
            relevant_metrics.append(metric_name)
    
    return relevant_metrics


def get_metric_config(metric_name: str) -> Dict:
    """Get configuration for a specific metric from utils/metrics.py."""
    metric_obj = METRIC_OBJECTS.get(metric_name)
    if not metric_obj:
        return {}
    
    # Extract configuration from the GEval metric object
    config = {
        "name": metric_obj.name,
        "evaluation_steps": metric_obj.evaluation_steps,
        "threshold": metric_obj.threshold,
        "evaluation_params": []
    }
    
    # Check evaluation_params
    if hasattr(metric_obj, 'evaluation_params'):
        params = metric_obj.evaluation_params
        if hasattr(params, '__iter__'):
            param_names = []
            for param in params:
                param_str = str(param)
                if "ACTUAL_OUTPUT" in param_str:
                    param_names.append("ACTUAL_OUTPUT")
                if "EXPECTED_OUTPUT" in param_str:
                    param_names.append("EXPECTED_OUTPUT")
            config["evaluation_params"] = param_names
    
    return config


def get_all_metric_names() -> List[str]:
    """Get all available custom metric names."""
    return list(METRIC_OBJECTS.keys())
