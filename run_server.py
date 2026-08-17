"""Single-port runner for the consolidated Clothing Sales Concierge & Catalog microservice."""

import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting unified clothing microservice on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
