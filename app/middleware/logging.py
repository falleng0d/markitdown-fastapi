import logging
import time
import uuid

from starlette.types import ASGIApp, Scope, Receive, Send, Message

logger = logging.getLogger("app.request")


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start = time.perf_counter()
        
        method = scope.get("method", "?")
        path = scope.get("path", "")
        query_string = (scope.get("query_string") or b"").decode("latin-1")
        
        headers = dict(scope.get("headers") or [])
        request_id = (headers.get(b"x-request-id") or b"").decode("latin-1").strip()
        if not request_id:
            request_id = str(uuid.uuid4())
        
        status_code: int | None = None
        
        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                
                # Add request id to response headers
                resp_headers = list(message.get("headers", []))
                resp_headers.append((b"x-request-id", request_id.encode("latin-1")))
                message["headers"] = resp_headers
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query": query_string,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise
        else:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "query": query_string,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
