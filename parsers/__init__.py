"""Parsers module — LLM output parsing and normalization.

Provides robust JSON extraction from raw LLM text and output normalization
to ensure compatibility with the Pydantic OutputSchema.

Functions:
    extract_json: Robust JSON extraction supporting objects and arrays.
    normalize_output: Normalize raw LLM dict to OutputSchema-compatible form.
"""
