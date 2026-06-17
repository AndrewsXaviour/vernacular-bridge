import json
import jsonschema
from pydantic import ValidationError
from models.contracts import OutputSchema
from validators.validators import compute_confidence_score, get_failure_reasons
from verification.adversarial_generator import generate_adversarial

def run_verification_case(case_type: str) -> dict:
    # 1. Generate adversarial output
    data = generate_adversarial(case_type)
    
    # Load JSON schema
    try:
        with open("schemas/output_schema.json", "r") as f:
            schema = json.load(f)
    except FileNotFoundError:
        schema = None

    # Results to capture
    result = {
        "pass_schema": False,
        "pass_pydantic": False,
        "actual_status": "success",
        "failure_reasons": [],
        "confidence_score": 0.0,
        "triggered_status": "none"  # success/retry/fallback based on detection
    }

    # 2a. JSON Schema Validation
    if schema:
        try:
            jsonschema.validate(instance=data, schema=schema)
            result["pass_schema"] = True
        except jsonschema.exceptions.ValidationError as e:
            result["failure_reasons"].append(f"JS_SCHEMA: {str(e).splitlines()[0]}")
    
    # 2b. Pydantic model validation
    try:
        model = OutputSchema(**data)
        result["pass_pydantic"] = True
        result["actual_status"] = model.status.value
        result["confidence_score"] = model.confidence_score
    except ValidationError as e:
        result["failure_reasons"].append(f"PYDANTIC: {str(e).splitlines()[0]}")

    # 3. Custom Validators
    if result["pass_pydantic"]:
        # Existing validators use the raw dict or the model data
        custom_reasons = get_failure_reasons(data)
        result["failure_reasons"].extend(custom_reasons)
        
        # Determine internal trigger status
        conf, breakdown = compute_confidence_score(data)
        result["confidence_score"] = conf
        
        # Logic to determine actual system behavior
        from validators.validators import STRUCTURAL_FAILURES
        
        # Add artificial schema/pydantic failure indicators if needed
        if not result["pass_schema"] or not result["pass_pydantic"]:
            if "SCHEMA_INVALID" not in result["failure_reasons"]:
                result["failure_reasons"].append("SCHEMA_INVALID")
        
        if any(reason in STRUCTURAL_FAILURES for reason in result["failure_reasons"]):
            result["triggered_status"] = "fallback"
        elif result["failure_reasons"]:
            result["triggered_status"] = "retry"
        else:
            result["triggered_status"] = "success"
    else:
        # If Pydantic failed, check if it's a structural issue
        result["failure_reasons"].append("SCHEMA_INVALID")
        result["triggered_status"] = "fallback"

    return result
