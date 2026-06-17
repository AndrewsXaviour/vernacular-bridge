import os
import time
from typing import List, Optional, Any, Dict
from google import genai
from google.genai import types
import json
import re
import asyncio
import logging
import uuid
from fastapi import FastAPI, HTTPException, Request, Response
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import traceback
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from models.request import QueryRequest, FullFlowRequest
from models.contracts import OutputSchema, Status, QuestionType
from models.coach import CoachRequest, CoachResponse
from models.navigator import NavigatorExplainRequest, NavigatorExplainResponse
from models.full_flow import FullFlowResponse
from utils.prompt_builder import build_prompt, build_coach_prompt
from utils.concept_resolver import resolve_concept
from validators.validators import compute_confidence_score, is_content_valid
from validators.coach_validator import normalize_coach_output, validate_coach_logic

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables (API Keys)
load_dotenv()

# Debug: Verify API key is loaded
api_key = os.getenv("GOOGLE_API_KEY")
print(
    f"DEBUG_API_KEY: {'Loaded' if api_key else 'None'} | Length: {len(api_key) if api_key else 0}"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA LOADING (Deterministic Retrieval) ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ENTITLEMENTS_PATH = os.path.join(DATA_DIR, "entitlements.json")
PROCESSES_PATH = os.path.join(DATA_DIR, "processes.json")

def load_json(path: str):
    if not os.path.exists(path):
        print(f"WARNING: Data file not found: {path}")
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load {path}: {e}")
        return []

# Cache in memory at startup
ENTITLEMENTS_DATA = load_json(ENTITLEMENTS_PATH)
PROCESSES_DATA = load_json(PROCESSES_PATH)

# --- ELITE IMPROVEMENTS STATE (Hardening 1 & 3) ---
LEARN_CACHE: Dict[str, dict] = {}
MAX_CACHE_SIZE = 100

class RateLimiter:
    """Non-blocking lightweight rate limiter."""
    def __init__(self, rpm: int = 20):
        self.rpm = rpm
        self.requests = []
        
    def is_allowed(self) -> bool:
        now = time.time()
        # Clean old timestamps (> 60s)
        self.requests = [t for t in self.requests if now - t < 60]
        if len(self.requests) >= self.rpm:
            return False
        self.requests.append(now)
        return True

# Per-IP Rate Limiting State (Elite+ Upgrade 2)
IP_LIMITS: Dict[str, RateLimiter] = {}

def check_rate_limit(ip: str) -> bool:
    if ip not in IP_LIMITS:
        IP_LIMITS[ip] = RateLimiter(rpm=20)
    return IP_LIMITS[ip].is_allowed()

# --- END ELITE STATE ---

# --- DETERMINISTIC RETRIEVAL & SAFETY ---

def normalize(value: Optional[str]) -> str:
    """Safe normalization: strip and lowercase. Returns empty string if value is None."""
    return value.strip().lower() if value else ""

class SafetyGuard:
    @staticmethod
    def extract_entities(data: Any) -> tuple[set[str], set[str]]:
        """Extracts all numbers and URLs from a dictionary or list."""
        if isinstance(data, dict) or isinstance(data, list):
            text = json.dumps(data, ensure_ascii=False)
        else:
            text = str(data)
            
        # Extract URLs
        # Improved to avoid trailing punctuation like periods or commas
        urls = set(re.findall(r'https?://[^\s<>"]+[a-zA-Z0-9/]', text))
        
        # Extract Numbers (removing commas for normalization)
        # Matches 1,000, 1000, 1000.50, etc.
        raw_numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', text)
        numbers = {n.replace(",", "") for n in raw_numbers}
        
        return urls, numbers

    @staticmethod
    def validate_fact_lock(input_data: dict, output_text: str) -> bool:
        """Verifies no new numbers or URLs are in the output."""
        in_urls, in_nums = SafetyGuard.extract_entities(input_data)
        out_urls, out_nums = SafetyGuard.extract_entities(output_text)
        
        # Check if output entities are a subset of input entities
        new_urls = out_urls - in_urls
        new_nums = out_nums - in_nums
        
        if new_urls:
            print(f"FACT-LOCK VIOLATION: New URLs detected: {new_urls}")
            return False
        if new_nums:
            # Avoid flagging empty numbers or single digits if they are common in language
            # but usually, strict subset is safer.
            print(f"FACT-LOCK VIOLATION: New Numbers detected: {new_nums} | Input Numbers: {in_nums}")
            return False
        return True

    @staticmethod
    def validate_keyword_lock(input_data: dict, output_text: str) -> bool:
        """Verifies core semantic meaning is preserved (Keywords Lock)."""
        important_fields = ["name", "eligibility", "benefits"]
        output_lower = output_text.lower()
        
        for field in important_fields:
            val = input_data.get(field)
            if not val:
                continue
            
            # Simple heuristic: ensure at least some meaningful part of the field is present
            # We look for words > 4 chars that are likely to be specific (not common stop words)
            words = [w.lower() for w in str(val).split() if len(w) > 4]
            if not words:
                continue # Skip if field is too short or generic
            
            # Check if at least one significant word is in the output
            if not any(word in output_lower for word in words):
                print(f"KEYWORD-LOCK VIOLATION: Field '{field}' missing from output.")
                return False
        return True

    @staticmethod
    def enforce_length_control(text: str, max_words: int) -> str:
        words = text.split()
        if len(words) > max_words:
            return " ".join(words[:max_words])
        return text

# --- RETRIEVAL RANKING (Hardening 2 & Upgrade 2) ---

def _retrieve_best_match(query: str) -> Optional[dict]:
    """
    Scored retrieval: Counts keyword matches across all datasets.
    Returns the item with the highest match count.
    """
    if not query:
        return None
        
    query_words = set(normalize(query).split())
    best_item = None
    max_score = 0
    
    # Combined search space
    all_data = ENTITLEMENTS_DATA + PROCESSES_DATA
    
    for item in all_data:
        # Score based on search_keywords
        keywords = [normalize(k) for k in item.get("search_keywords", [])]
        score = sum(1 for word in query_words if any(word in kw for kw in keywords))
        
        # Tie-breaker or boost if query is exactly in the name
        if normalize(query) in normalize(item.get("name", "")):
            score += 2
            
        if score > max_score:
            max_score = score
            best_item = item
            
    # Return only if we have a meaningful match
    return best_item if max_score > 0 else None

# --- END DATA LOADING ---

# SDK Migration: Using new google-genai Client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# CIRCUIT BREAKER STATE
USE_PRIMARY = True
PRIMARY_MODEL = "gemini-2.5-flash"
SECONDARY_MODEL = "gemini-2.5-pro"


def is_quota_error(e: Exception) -> bool:
    """
    Detects quota-related failures (429 / RESOURCE_EXHAUSTED).
    """
    err_str = str(e).upper()
    return "429" in err_str or "RESOURCE_EXHAUSTED" in err_str


def call_gemini(model_name: str, prompt: str) -> str:
    """
    Single responsibility Gemini API call.
    """
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
    except Exception as e:
        print(
            f"GEMINI_EXCEPTION | model={model_name} | error={type(e).__name__} | msg={str(e)}"
        )
        raise

    # Gap 1: Empty Content Guard - check for empty/whitespace-only
    if not response.text or not response.text.strip():
        raise ValueError(f"Empty response from {model_name}")
    return response.text


async def async_call_gemini(model_name: str, prompt: str) -> str:
    """
    Async implementation of Gemini API call using client.aio.
    """
    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
        )
    except Exception as e:
        logger.error(
            f"ASYNC_GEMINI_EXCEPTION | model={model_name} | error={type(e).__name__} | msg={str(e)}"
        )
        raise

    if not response.text or not response.text.strip():
        raise ValueError(f"Empty response from {model_name}")
    return response.text


def get_best_model(client) -> str:
    """
    Dynamically discovers and selects the best available Gemini model.
    Priority:
    1. Prefer 'gemini-flash-latest' if available
    2. Fallback to any 'flash' model
    3. Fallback to any model supporting generateContent
    """
    try:
        models = list(client.models.list())

        # 1. Filter only models that support generateContent
        # NOTE: Using 'supported_actions' for the v1beta SDK
        valid_models = [
            m.name
            for m in models
            if "generateContent" in getattr(m, "supported_actions", [])
        ]

        # TASK 5: Print all available models once at startup
        print("AVAILABLE GEMINI MODELS:", valid_models)

        if not valid_models:
            raise RuntimeError("No compatible Gemini model found for generateContent")

        # TASK 3: IMPLEMENT PRIORITY LOGIC

        # 1. Prefer "gemini-flash-latest"
        for preferred in ["gemini-flash-latest"]:
            for m_name in valid_models:
                if preferred in m_name:
                    print("SELECTED MODEL:", m_name)
                    return m_name

        # 2. Else fallback to any "flash" model
        for m_name in valid_models:
            if "flash" in m_name.lower():
                print("SELECTED MODEL:", m_name)
                return m_name

        # 3. Else fallback to any model supporting generateContent
        print("SELECTED MODEL (Fallback):", valid_models[0])
        return valid_models[0]

    except Exception as e:
        print(f"CRITICAL: No compatible Gemini model found: {e}")
        raise RuntimeError(f"No compatible Gemini model found for generateContent: {e}")


# Fix 1: Honest Fallback (Honest Failure)
SAFE_FALLBACK_JSON = {
    "status": "error",
    "message": "Unable to generate accurate content. Please try again.",
}


def generate_from_llm(prompt: str):
    """
    Gemini-only fallback:
    1. Primary (gemini-3-flash)
    2. Secondary (gemini-flash-latest) on failure or quota
    3. Final safe JSON fallback
    """
    global USE_PRIMARY

    # 1. PRIMARY EXECUTION
    if USE_PRIMARY:
        for attempt in range(1, 4):  # Attempt 1, then up to 2 retries
            start_time = time.time()
            try:
                text = call_gemini(PRIMARY_MODEL, prompt)
                duration = time.time() - start_time
                print(
                    f"LLM_PRIMARY_SUCCESS | model={PRIMARY_MODEL} | time={duration:.2f}s | length={len(text)}"
                )
                return text

            except Exception as e:
                duration = time.time() - start_time
                if is_quota_error(e):
                    # QUOTA ERROR: Skip retries, flip circuit breaker, move to secondary
                    USE_PRIMARY = False
                    print(
                        f"LLM_ERROR | model={PRIMARY_MODEL} | type=quota | msg={str(e)}"
                    )
                    print(f"LLM_FALLBACK_FLASH_LATEST | reason=quota_exhausted")
                    break  # Out of retry loop to secondary

                # NON-QUOTA ERROR: Retry logic
                if attempt < 3:
                    print(
                        f"LLM_RETRY_ATTEMPT | model={PRIMARY_MODEL} | attempt={attempt} | type=sdk_or_network"
                    )
                    time.sleep(1)  # Reduce from 12s to 1s for hackathon demo compatibility
                else:
                    # All retries failed
                    print(
                        f"LLM_ERROR | model={PRIMARY_MODEL} | type=exhausted_retries | time={duration:.2f}s"
                    )
                    print(
                        f"LLM_FALLBACK_FLASH_LATEST | reason=primary_failed_after_retries"
                    )

    # 2. SECONDARY EXECUTION
    start_time = time.time()
    try:
        text = call_gemini(SECONDARY_MODEL, prompt)
        duration = time.time() - start_time
        print(f"LLM_SECONDARY_SUCCESS | model={SECONDARY_MODEL} | time={duration:.2f}s")
        return text
    except Exception as e:
        duration = time.time() - start_time
        error_type = "quota" if is_quota_error(e) else "other"
        print(
            f"LLM_ERROR | model={SECONDARY_MODEL} | type={error_type} | time={duration:.2f}s"
        )

    # 3. FINAL SAFETY FALLBACK
    print(f"LLM_FINAL_FALLBACK | status=zero_failure_demo_mode")
    return json.dumps(SAFE_FALLBACK_JSON)


async def async_generate_from_llm(prompt: str):
    """
    Async wrapper that uses synchronous call_gemini in a thread pool 
    to avoid aiohttp/DNS issues in restricted environments.
    """
    loop = asyncio.get_event_loop()
    # Run the synchronous generate_from_llm in a thread
    return await loop.run_in_executor(None, generate_from_llm, prompt)


async def safe_call(coro, module_name: str, timeout: int = 15):
    """
    Hardening: Timeout wrapper with exception handling and logging.
    """
    try:
        logger.info(f"MODULE_{module_name}_START")
        result = await asyncio.wait_for(coro, timeout=timeout)
        logger.info(f"MODULE_{module_name}_SUCCESS")
        return result
    except asyncio.TimeoutError:
        logger.warning(f"MODULE_{module_name}_TIMEOUT")
        return None
    except Exception as e:
        try:
            logger.error(f"MODULE_{module_name}_FAILED | error={str(e)}")
        except:
            pass
        return None


def generate_with_timeout(prompt: str) -> str:
    """
    Compatibility wrapper for legacy calls.
    Now uses the robust generate_from_llm logic.
    """
    return generate_from_llm(prompt)


def extract_json(text: str):
    """
    Robust JSON extraction from LLM response.
    Supports both objects {} and arrays [].
    """
    if not isinstance(text, str):
        return text  # Already parsed or error dict

    # Attempt direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # Detect JSON type boundaries
    first_curly = text.find("{")
    last_curly = text.rfind("}")
    first_square = text.find("[")
    last_square = text.rfind("]")

    # Choose whichever appears first as the root
    if first_curly != -1 and (first_square == -1 or first_curly < first_square):
        start, end = first_curly, last_curly
    elif first_square != -1:
        start, end = first_square, last_square
    else:
        raise ValueError("No JSON object or array found in response")

    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except Exception as e:
            raise ValueError(f"JSON extraction failed after slicing: {e}")

    raise ValueError("Invalid JSON boundaries")


def safe_json_loads(text: str):
    """
    Legacy wrapper refactored to use robust extraction logic.
    """
    try:
        return extract_json(text)
    except Exception as e:
        print(f"DEBUG: safe_json_loads failed: {e}")
        return None


def regenerate_mcqs(user_input: str) -> list:
    prompt = f"""
Generate exactly 3 MCQs for the topic: {user_input}.

STRICT RULES:
- Return ONLY JSON array
- Each MCQ must have:
  - question (string)
  - options (exactly 4 strings)
  - answer (must match one option exactly)
- No explanation
"""
    try:
        raw = generate_with_timeout(prompt)
        if not raw:
            return []

        # Use robust extraction instead of non-greedy array regex
        parsed = extract_json(raw)
        if isinstance(parsed, list):
            return parsed
    except Exception as e:
        print(f"DEBUG: regenerate_mcqs extraction failed: {e}")
    return []


def normalize_output(data: dict) -> dict:
    """
    Normalize LLM output to ensure OutputSchema compatibility.
    Handles schema mismatches, missing fields, and malformed data.
    """
    if not isinstance(data, dict):
        data = {}

    result = {}

    # A. TEXT FIELDS
    result["tamil_simple"] = str(data.get("tamil_simple", "")).strip()
    result["english_academic"] = str(data.get("english_academic", "")).strip()

    # B. STEPS
    raw_steps = data.get("steps")
    if isinstance(raw_steps, list):
        steps = [str(s).strip() for s in raw_steps if s]
    elif isinstance(raw_steps, str) and raw_steps.strip():
        steps = [raw_steps.strip()]
    else:
        steps = []
    result["steps"] = steps

    # Fix 2: Quality Guard (Block Generic / Empty)
    if not result["tamil_simple"].strip() or not result["english_academic"].strip():
        raise ValueError("Empty content generated")

    generic_phrases = [
        "identify the concept",
        "break down",
        "core idea",
        "key components",
        "in simple terms",
    ]

    for phrase in generic_phrases:
        if phrase in result["tamil_simple"].lower() or phrase in result["english_academic"].lower():
            raise ValueError(f"Generic content detected: {phrase}")
        for step in result["steps"]:
            if phrase in step.lower():
                raise ValueError(f"Generic content detected in steps: {phrase}")

    if len(result["steps"]) < 2:
        raise ValueError("Insufficient steps generated")

    # C. QUESTION DECODER
    raw_qd = data.get("question_decoder")
    if not isinstance(raw_qd, dict):
        raw_qd = {}

    qd = {
        "question_type": str(raw_qd.get("question_type", "explain")).lower(),
        "expected_structure": str(raw_qd.get("expected_structure", "")).strip(),
        "answer_template": str(raw_qd.get("answer_template", "")).strip(),
    }

    # Map to valid QuestionType
    mapping = {
        "process explanation": "explain",
        "detailed explanation": "explain",
        "how it works": "explain",
        "definition": "define",
        "what is": "define",
        "comparison": "compare",
        "contrast": "compare",
        "difference": "compare",
        "analysis": "analyze",
        "evaluation": "analyze",
        "diagram": "diagram",
        "visual representation": "diagram",
        "short note": "short_note",
    }
    qd["question_type"] = mapping.get(qd["question_type"], qd["question_type"])
    valid_types = [t.value for t in QuestionType]
    if qd["question_type"] not in valid_types:
        qd["question_type"] = "explain"

    result["question_decoder"] = qd

    # D. MCQs (CRITICAL)
    raw_mcqs = data.get("mcqs")
    clean_mcqs = []

    if isinstance(raw_mcqs, list):
        for mcq in raw_mcqs:
            if not isinstance(mcq, dict):
                continue

            # Normalize correct_answer from any key
            correct = None
            for key in ("correct_answer", "answer", "correct"):
                if key in mcq and mcq[key]:
                    correct = str(mcq[key])
                    break

            # Ensure question is string
            question = str(mcq.get("question", "")).strip()
            if not question:
                continue

            # Normalize options to list of strings
            raw_options = mcq.get("options")
            if isinstance(raw_options, list):
                options = [str(opt).strip() for opt in raw_options if opt]
            elif isinstance(raw_options, str):
                options = [opt.strip() for opt in raw_options.split("|") if opt.strip()]
            else:
                options = []

            # Remove duplicates while preserving order
            seen = set()
            unique_options = []
            for opt in options:
                if opt.lower() not in seen:
                    seen.add(opt.lower())
                    unique_options.append(opt)
            options = unique_options

            # Skip if less than 4 options
            if len(options) < 4:
                continue

            # If correct_answer not in options, append it (per requirement)
            appended = False
            if correct and correct not in options:
                options.append(correct)
                appended = True

            # Final validation: must have at least 4 options
            if len(options) < 4:
                continue

            # If we appended correct_answer, keep all options (don't slice to 4)
            final_options = options if appended else options[:4]

            clean_mcqs.append(
                {
                    "question": question,
                    "options": final_options,
                    "correct_answer": correct,
                }
            )

    result["mcqs"] = clean_mcqs[:5]

    # Debug log
    print("NORMALIZED OUTPUT:", json.dumps(result, indent=2, ensure_ascii=True))

    return result


@app.post("/learn")
async def learn_content(request: QueryRequest):
    result = await _internal_learn(request.user_input, request.language_config)
    if not result:
        return SAFE_FALLBACK_JSON
    return result


@app.post("/coach")
async def coach_answer(request: CoachRequest):
    """
    Evaluates a student's answer using a strict academic rubric.
    """
    result = await _internal_coach(request.question, request.student_answer, request.language_config)
    if not result:
        return {
            "score": 0,
            "structure_feedback": "Unable to evaluate answer due to a system error.",
            "missing_points": ["System Error"],
            "language_feedback": "Error processing request.",
            "improved_answer": "System encountered an error during evaluation. Please try again."
        }
    return result


# --- ASYNC INTERNAL HELPERS (Unified Orchestration) ---

async def _internal_learn(query: str, lang_config: Any) -> Optional[dict]:
    """
    Internal logic for /learn module with Language-Aware Caching & TTL (Elite+ Upgrade 1).
    """
    # 1. Check Cache with TTL (Elite Upgrade 1 & Tune 1)
    cache_key = f"{query}_{lang_config.primary}_{lang_config.secondary}".lower()
    now = time.time()
    
    if cache_key in LEARN_CACHE:
        entry = LEARN_CACHE[cache_key]
        if now < entry["expiry"]:
            logger.info(f"CACHE_HIT | key={cache_key}")
            return entry["data"]
        else:
            logger.info(f"CACHE_EXPIRED | key={cache_key}")
            LEARN_CACHE.pop(cache_key)
        
    # 2. Proceed with LLM
    concept, tamil_anchor, source = resolve_concept(query)
    prompt = build_prompt(
        concept=concept,
        domain="Academic",
        primary_lang=lang_config.primary,
        secondary_lang=lang_config.secondary
    )
    
    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None
        
    normalized = normalize_output(parsed)
    validated = OutputSchema.model_validate(normalized)
    result = validated.model_dump()
    
    # 3. Save to Cache with TTL (Tune 2 & Elite+ 1)
    if len(LEARN_CACHE) >= MAX_CACHE_SIZE:
        try:
            first_key = next(iter(LEARN_CACHE))
            LEARN_CACHE.pop(first_key)
        except StopIteration:
            pass
            
    LEARN_CACHE[cache_key] = {
        "data": result,
        "expiry": now + 600 # 10 minute TTL
    }
    return result


async def _internal_coach(question: str, student_answer: str, lang_config: Any) -> Optional[dict]:
    """
    Internal logic for /coach module.
    """
    prompt = build_coach_prompt(
        question=question,
        student_answer=student_answer,
        primary_lang=lang_config.primary,
        secondary_lang=lang_config.secondary
    )
    
    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None
        
    normalized = normalize_coach_output(parsed)
    validated_logic = validate_coach_logic(normalized)
    validated = CoachResponse.model_validate(validated_logic)
    return validated.model_dump()


async def _internal_navigator_explain(item: dict, lang_config: Any) -> Optional[dict]:
    """
    Internal logic for /navigator/explain module.
    """
    prompt = f"""
EXPLAIN the following dataset item in TWO languages:
1. Primary: Simple {lang_config.primary} (explanation_primary)
2. Secondary: Academic {lang_config.secondary} (summary_secondary)

INPUT DATA:
{json.dumps(item, indent=2)}

STRICT RULES:
- You MUST ONLY use the information provided in the input JSON.
- Do NOT add any new facts, examples, or assumptions.
- Return ONLY a JSON object with keys: "explanation_primary", "summary_secondary".
"""
    raw_response = await async_generate_from_llm(prompt)
    parsed = extract_json(raw_response)
    if not parsed:
        return None
        
    primary = str(parsed.get("explanation_primary", ""))
    secondary = str(parsed.get("summary_secondary", ""))
    
    # Safety Guards
    combined_output = f"{primary} {secondary}"
    if not SafetyGuard.validate_fact_lock(item, combined_output):
        return None
    if not SafetyGuard.validate_keyword_lock(item, combined_output):
        return None
        
    return {
        "explanation_primary": SafetyGuard.enforce_length_control(primary, 120),
        "summary_secondary": SafetyGuard.enforce_length_control(secondary, 80)
    }


@app.post("/generate")
def generate_legacy(request: QueryRequest):
    """
    Legacy alias for /learn endpoint.
    """
    return learn_content(request)


@app.post("/full-flow", response_model=FullFlowResponse)
async def full_flow(request: FullFlowRequest, fastapi_request: Request, response: Response):
    """
    Unified orchestration endpoint.
    Runs Learn, Coach, and Navigator in parallel with strict timeouts.
    Includes Elite Improvements: Caching, Request ID, and Per-IP Rate Limiting.
    """
    # 1. Per-IP Rate Limiting (Elite+ Upgrade 2)
    client_ip = fastapi_request.client.host if fastapi_request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"RATE_LIMIT_EXCEEDED | ip={client_ip}")
        raise HTTPException(status_code=422, detail="Too Many Requests from this IP. Please try again in a minute.")
        
    # 2. Request ID Tracking (Elite Upgrade 2)
    req_id = str(uuid.uuid4())[:8] # Short UUID for logging readability
    logger.info(f"[{req_id}] FULL_FLOW_START | ip={client_ip} | query={request.query[:50]}...")
    
    # helper for prefixed logging
    def log(msg, level="info"):
        final_msg = f"[{req_id}] {msg}"
        if level == "warning": logger.warning(final_msg)
        elif level == "error": logger.error(final_msg)
        else: logger.info(final_msg)
    
    # 1. Prepare Tasks
    tasks = []
    task_keys = []
    
    # MODULE: Learn (Always)
    tasks.append(safe_call(_internal_learn(request.query, request.language_config), "LEARN"))
    task_keys.append("learning")
    
    # MODULE: Coach (Conditional)
    if request.student_answer:
        tasks.append(safe_call(_internal_coach(request.query, request.student_answer, request.language_config), "COACH"))
        task_keys.append("evaluation")
    else:
        tasks.append(asyncio.sleep(0, result=None)) # Dummy task
        task_keys.append("evaluation") # Will be None
        
    # MODULE: Navigator (Conditional)
    if request.use_navigator:
        # Dependency check: Retrieve match first
        match = _retrieve_best_match(request.query)
        if match:
            tasks.append(safe_call(_internal_navigator_explain(match, request.language_config), "NAVIGATOR"))
        else:
            log("NAVIGATOR_NO_MATCH_FOUND", "info")
            tasks.append(asyncio.sleep(0, result=None))
    else:
        tasks.append(asyncio.sleep(0, result=None))
    task_keys.append("navigator")

    # 2. Parallel Execution (return_exceptions=True for Hardening 1)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 3. Process Results (Hardening 1 & 3)
    final_output = {
        "learning": None,
        "evaluation": None,
        "navigator": None
    }
    
    for key, result in zip(task_keys, results):
        if isinstance(result, Exception):
            log(f"MODULE_{key.upper()}_EXCEPTION | msg={str(result)}", "error")
            final_output[key] = None
        else:
            final_output[key] = result
            
    log("FULL_FLOW_COMPLETE", "info")
    return FullFlowResponse(**final_output)


@app.get("/health")
async def health_check():
    """
    Health Monitoring (Elite+ Upgrade 3).
    """
    return {
        "status": "ok", 
        "timestamp": time.time(),
        "version": "1.0.0",
        "cache_size": len(LEARN_CACHE),
        "active_ips": len(IP_LIMITS)
    }


# --- RETRIEVAL ENDPOINTS ---

@app.get("/entitlements")
def get_entitlements(
    category: Optional[str] = None,
    applicable_for: Optional[str] = None,
    keyword: Optional[str] = None
):
    results = ENTITLEMENTS_DATA
    
    # 1. Category Filter (Case-insensitive match in array)
    if category:
        q_cat = normalize(category)
        results = [
            item for item in results 
            if q_cat in [normalize(c) for c in item.get("category", [])]
        ]
        
    # 2. Applicable For Filter (Case-insensitive exact match)
    if applicable_for:
        q_app = normalize(applicable_for)
        results = [
            item for item in results 
            if normalize(item.get("applicable_for")) == q_app
        ]
        
    # 3. Keyword Filter (Case-insensitive contains in search_keywords array)
    if keyword and normalize(keyword):
        q_key = normalize(keyword)
        results = [
            item for item in results 
            if any(q_key in normalize(k) for k in item.get("search_keywords", []))
        ]
        
    # Safeguard: Ensure unique results by name
    results = list({item["name"]: item for item in results}.values())
    
    return {
        "count": len(results),
        "results": results
    }


@app.get("/processes")
def get_processes(
    keyword: Optional[str] = None
):
    results = PROCESSES_DATA
    
    # 1. Keyword Filter (Case-insensitive contains in search_keywords array)
    if keyword and normalize(keyword):
        q_key = normalize(keyword)
        results = [
            item for item in results 
            if any(q_key in normalize(k) for k in item.get("search_keywords", []))
        ]
        
    # Safeguard: Ensure unique results by name
    results = list({item["name"]: item for item in results}.values())
    
    return {
        "count": len(results),
        "results": results
    }

# --- END RETRIEVAL ENDPOINTS ---


@app.post("/navigator/explain", response_model=NavigatorExplainResponse)
async def explain_item(request: NavigatorExplainRequest):
    """
    Bilingual explanation of a dataset item with strict Fact-Lock hallucination protection.
    """
    # Use default language config if not provided in request (not in schema yet, but good practice)
    from models.request import LanguageConfig
    lang_config = LanguageConfig()
    
    result = await _internal_navigator_explain(request.item, lang_config)
    if not result:
        raise HTTPException(status_code=422, detail="Safety check failed or LLM error.")
        
    return NavigatorExplainResponse(**result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
