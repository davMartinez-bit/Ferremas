from fastapi import Request, Response
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging

logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path
    
    if method == "OPTIONS":
        logger.debug(f"CORS Preflight: {method} {path}")
        response = await call_next(request)
        return response
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        formatted_time = f"{process_time:.2f}"
        
        logger.info(
            f"Method={method} "
            f"Path={path} "
            f"Status={response.status_code} "
            f"Time={formatted_time}ms "
            f"Client={request.client.host if request.client else 'unknown'}"
        )
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"ERROR - Method={method} "
            f"Path={path} "
            f"Time={process_time:.2f}ms "
            f"Error={str(e)}"
        )
        raise

async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if request.method != "OPTIONS":
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if not getattr(request.app.state, 'debug', True):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

def setup_middlewares(app):
    app.middleware("http")(security_headers)
    app.middleware("http")(log_requests)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    logger.info("✅ Middlewares configurados correctamente")