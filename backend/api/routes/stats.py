from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Header, Query, Request

from api.shared import ensure_web_or_device_access
from core.auth import decode_session_token, require_admin
from core.stats_store import (
    get_admin_console_summary,
    get_device_stats,
    get_render_history,
    get_stats_overview,
    log_site_visit,
)

router = APIRouter(tags=["stats"])


def _optional_user_id_from_session(ink_session: Optional[str]) -> Optional[int]:
    if not ink_session:
        return None
    payload = decode_session_token(ink_session)
    if not payload or "sub" not in payload:
        return None
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        return None


@router.get("/stats/overview")
async def stats_overview(admin_auth: None = Depends(require_admin)):
    return await get_stats_overview()


@router.get("/admin/console/summary")
async def admin_console_summary(admin_auth: None = Depends(require_admin)):
    return await get_admin_console_summary()


@router.post("/analytics/pageview")
async def analytics_pageview(
    body: dict,
    request: Request,
    ink_session: Optional[str] = Cookie(default=None),
):
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip = forwarded_for.split(",", 1)[0].strip() if forwarded_for else (request.client.host if request.client else "")
    await log_site_visit(
        path=str(body.get("path") or request.headers.get("referer") or "/"),
        method="GET",
        host=request.headers.get("host", ""),
        referrer=request.headers.get("referer", ""),
        user_agent=request.headers.get("user-agent", ""),
        ip=ip,
        user_id=_optional_user_id_from_session(ink_session),
        mac=str(body.get("mac") or ""),
        source=str(body.get("source") or "web"),
    )
    return {"ok": True}


@router.get("/stats/{mac}")
async def stats_device(
    mac: str,
    request: Request,
    x_device_token: Optional[str] = Header(default=None),
    ink_session: Optional[str] = Cookie(default=None),
):
    await ensure_web_or_device_access(request, mac, x_device_token, ink_session)
    return await get_device_stats(mac)


@router.get("/stats/{mac}/renders")
async def stats_renders(
    mac: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    x_device_token: Optional[str] = Header(default=None),
    ink_session: Optional[str] = Cookie(default=None),
):
    await ensure_web_or_device_access(request, mac, x_device_token, ink_session)
    return {"mac": mac, "renders": await get_render_history(mac, limit, offset)}
