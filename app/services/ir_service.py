import importlib.util
import secrets
import time
from functools import lru_cache
from pathlib import Path
from threading import Lock


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RETRIEVAL_DIR = PROJECT_ROOT / "src" / "retrieval"

VERIFICATION_TTL_SECONDS = 900
_verification_sessions = {}
_verification_lock = Lock()


def load_module(filename, module_name):
    """Load an existing research module without modifying its source."""
    module_path = RETRIEVAL_DIR / filename

    if not module_path.is_file():
        raise FileNotFoundError(
            f"Retrieval module not found: {module_path}"
        )

    spec = importlib.util.spec_from_file_location(
        module_name,
        module_path,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load retrieval module: {module_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


@lru_cache(maxsize=1)
def get_ir_engine():
    """Initialize and cache the medication retrieval components."""
    matching = load_module(
        "02_medication_name_matching.py",
        "mom_u_medication_matching",
    )

    recognition = load_module(
        "06_medication_entity_recognition.py",
        "mom_u_medication_recognition",
    )

    resolution = load_module(
        "08_medication_candidate_resolution.py",
        "mom_u_medication_resolution",
    )

    verification = load_module(
        "09_medication_identity_verification.py",
        "mom_u_medication_verification",
    )

    retrieval = load_module(
        "10_verified_medication_retrieval.py",
        "mom_u_verified_retrieval",
    )

    medications = matching.load_medications()
    document_index = retrieval.load_document_index()

    return {
        "matching": matching,
        "recognition": recognition,
        "resolution": resolution,
        "verification": verification,
        "retrieval": retrieval,
        "medications": medications,
        "document_index": document_index,
    }


def resolve_medication_query(query):
    """Resolve a user query into medication candidates."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Medication query cannot be empty.")

    engine = get_ir_engine()

    return engine["resolution"].resolve_medication(
        query.strip(),
        engine["medications"],
        engine["matching"],
        engine["recognition"],
    )


def prepare_medication_verification(query):
    """Prepare medication candidates for explicit user confirmation."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Medication query cannot be empty.")

    engine = get_ir_engine()

    verification = engine["verification"].prepare_verification(
        query.strip(),
        engine["resolution"],
        engine["medications"],
        engine["matching"],
        engine["recognition"],
    )

    if not verification["candidates"]:
        verification["requires_user_confirmation"] = False

    return verification


def _remove_expired_sessions():
    """Remove expired verification sessions."""
    now = time.monotonic()

    expired_tokens = [
        token
        for token, session in _verification_sessions.items()
        if now >= session["expires_at"]
    ]

    for token in expired_tokens:
        _verification_sessions.pop(token, None)


def create_verification_session(query):
    """Create a temporary server-side verification session."""
    verification = prepare_medication_verification(query)

    if not verification["candidates"]:
        return {
            "verification": verification,
            "verification_token": None,
            "expires_in_seconds": None,
        }

    token = secrets.token_urlsafe(32)

    with _verification_lock:
        _remove_expired_sessions()

        _verification_sessions[token] = {
            "verification": verification,
            "expires_at": time.monotonic() + VERIFICATION_TTL_SECONDS,
        }

    return {
        "verification": verification,
        "verification_token": token,
        "expires_in_seconds": VERIFICATION_TTL_SECONDS,
    }


def confirm_verification_session(token, selected_document_ids):
    """Confirm selected candidates using a server-side verification session."""
    if not isinstance(token, str) or not token.strip():
        raise ValueError("Verification token is required.")

    if (
        not isinstance(selected_document_ids, list)
        or not selected_document_ids
    ):
        raise ValueError("At least one medication must be selected.")

    with _verification_lock:
        _remove_expired_sessions()

        session = _verification_sessions.get(token)

        if session is None:
            raise ValueError(
                "Verification token is invalid, expired, or already used."
            )

        engine = get_ir_engine()

        verification = engine["verification"].confirm_medications(
            session["verification"],
            selected_document_ids,
        )

        records = engine["retrieval"].retrieve_verified_medications(
            verification,
            engine["document_index"],
        )

        _verification_sessions.pop(token, None)

    return {
        "verification": verification,
        "records": records,
    }
