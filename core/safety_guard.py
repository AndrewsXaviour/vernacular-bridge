"""Safety guards for LLM output validation.

Provides hallucination prevention via Fact-Lock (no new numbers/URLs)
and Keyword-Lock (core semantic meaning preserved), plus length control
to cap output verbosity.

Classes:
    SafetyGuard: Static methods for output validation and control.
"""

import json
import re
from typing import Any


class SafetyGuard:
    """Static safety guards for navigator/explain output validation.

    Methods:
        extract_entities: Extract URLs and numbers from data.
        validate_fact_lock: Ensure no hallucinated numbers or URLs.
        validate_keyword_lock: Ensure core keywords are preserved.
        enforce_length_control: Truncate text to a maximum word count.
    """

    @staticmethod
    def extract_entities(data: Any) -> tuple[set[str], set[str]]:
        """Extract all URLs and numbers from a dictionary, list, or string.

        Args:
            data: The input data to scan.

        Returns:
            A tuple of (urls, numbers) as sets of strings.
        """
        if isinstance(data, dict) or isinstance(data, list):
            text = json.dumps(data, ensure_ascii=False)
        else:
            text = str(data)

        urls = set(re.findall(r'https?://[^\s<>"]+[a-zA-Z0-9/]', text))
        raw_numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
        numbers = {n.replace(",", "") for n in raw_numbers}

        return urls, numbers

    @staticmethod
    def validate_fact_lock(input_data: dict, output_text: str) -> bool:
        """Verify no new numbers or URLs appear in the output.

        Args:
            input_data: The original data provided as input.
            output_text: The generated output text.

        Returns:
            True if the output passes the fact-lock check.
        """
        in_urls, in_nums = SafetyGuard.extract_entities(input_data)
        out_urls, out_nums = SafetyGuard.extract_entities(output_text)

        new_urls = out_urls - in_urls
        new_nums = out_nums - in_nums

        if new_urls:
            print(f"FACT-LOCK VIOLATION: New URLs detected: {new_urls}")
            return False
        if new_nums:
            print(f"FACT-LOCK VIOLATION: New Numbers detected: {new_nums} | Input Numbers: {in_nums}")
            return False
        return True

    @staticmethod
    def validate_keyword_lock(input_data: dict, output_text: str) -> bool:
        """Verify core semantic meaning is preserved via keyword matching.

        Checks that at least one significant word (>4 chars) from each
        important field (name, eligibility, benefits) appears in the output.

        Args:
            input_data: The original data provided as input.
            output_text: The generated output text.

        Returns:
            True if the output passes the keyword-lock check.
        """
        important_fields = ["name", "eligibility", "benefits"]
        output_lower = output_text.lower()

        for field in important_fields:
            val = input_data.get(field)
            if not val:
                continue

            words = [w.lower() for w in str(val).split() if len(w) > 4]
            if not words:
                continue

            if not any(word in output_lower for word in words):
                print(f"KEYWORD-LOCK VIOLATION: Field '{field}' missing from output.")
                return False
        return True

    @staticmethod
    def enforce_length_control(text: str, max_words: int) -> str:
        """Truncate text to a maximum number of words.

        Args:
            text: The input text.
            max_words: Maximum number of words to keep.

        Returns:
            The truncated text.
        """
        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words])
        return text
