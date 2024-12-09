from canvasserver.constants import APP_NAME
from canvasserver.routes import api_router
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title=APP_NAME)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")
