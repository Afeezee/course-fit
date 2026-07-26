"""
auth.py
-------
Clerk JWT verification. Verifies the short-lived JWT that Clerk's
Next.js SDK issues to a signed-in browser and returns the Clerk user
ID (the `sub` claim) if valid, or None if the token is absent, wrong
issuer, expired, or the signature can't be verified.

Deliberate design decisions:
  - Fail-open on absence: anonymous requests (no Authorization header)
    return None so /api/recommend still works for signed-out users.
  - Fail-closed on invalid: a *present but bad* token raises 401 —
    someone actively trying to forge auth should not get through.
  - JWKS cached in-process via PyJWKClient's built-in cache; a Clerk
    key rotation is picked up on the next cache expiry (default 1 h)
    so no restart is needed.

Env var:
  CLERK_ISSUER — the Frontend API base URL from your Clerk dashboard,
  e.g. https://neat-koala-42.clerk.accounts.dev (dev) or
  https://clerk.your-domain.com (prod). If unset, the module short-
  circuits and every request is treated as anonymous.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import Header, HTTPException

log = logging.getLogger("courselab.auth")

_jwks_client = None
_issuer: Optional[str] = None


def _get_jwks_client():
    """Lazily build (and cache) the JWKS client. Returns None if the
    Clerk issuer isn't configured or PyJWT can't be imported."""
    global _jwks_client, _issuer
    if _jwks_client is not None:
        return _jwks_client
    issuer = os.environ.get("CLERK_ISSUER", "").strip().rstrip("/")
    if not issuer:
        return None
    try:
        from jwt import PyJWKClient
    except ImportError:
        log.warning("PyJWT not installed — auth disabled")
        return None
    try:
        _jwks_client = PyJWKClient(f"{issuer}/.well-known/jwks.json")
        _issuer = issuer
        return _jwks_client
    except Exception as e:
        log.warning("failed to init Clerk JWKS client: %s", e)
        return None


def is_enabled() -> bool:
    return _get_jwks_client() is not None


def _decode(token: str) -> dict:
    import jwt

    jwks = _get_jwks_client()
    if jwks is None:
        raise HTTPException(status_code=503, detail="auth not configured")

    try:
        signing_key = jwks.get_signing_key_from_jwt(token).key
        # Clerk JWTs use RS256. Skip audience check — Clerk uses `azp`
        # for the authorized party, and issuer check is what actually
        # binds a token to your Clerk app.
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=_issuer,
            options={"verify_aud": False},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.InvalidTokenError as e:
        # Log the concrete reason so misconfigurations are diagnosable
        # (issuer mismatch, wrong audience, key rotation, etc.).
        log.warning("invalid token: %s: %s", type(e).__name__, e)
        try:
            unverified = jwt.decode(token, options={"verify_signature": False})
            log.warning(
                "  token iss=%r sub=%r azp=%r",
                unverified.get("iss"),
                unverified.get("sub"),
                unverified.get("azp"),
            )
        except Exception:
            pass
        log.warning("  expected iss=%r", _issuer)
        raise HTTPException(status_code=401, detail="invalid token")


def optional_user_id(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    """FastAPI dependency: returns the Clerk user_id if a valid token
    is present, or None if no token is present. Raises 401 if a token
    is present but invalid — that means someone tried to forge auth."""
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        # Malformed header — treat as absent rather than forgery.
        return None
    token = parts[1].strip()
    if not is_enabled():
        # Client sent a token but the server isn't configured to
        # verify. Treat as anonymous — safer than accepting blind.
        return None
    payload = _decode(token)
    return str(payload.get("sub") or "") or None


def required_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    """FastAPI dependency: like optional_user_id but 401s if no token
    is present or the token is invalid. Use for endpoints that only
    make sense for signed-in users (e.g. /api/history)."""
    uid = optional_user_id(authorization)
    if not uid:
        raise HTTPException(status_code=401, detail="sign-in required")
    return uid
