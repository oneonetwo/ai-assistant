from fastapi import Request
import time
from typing import Callable
import logging

logger = logging.getLogger(__name__)

async def document_processing_middleware(
    request: Request,
    call_next: Callable
):
    if request.url.path.startswith("/documents"):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"Document processing took {process_time:.2f} seconds")
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    return await call_next(request) 