from fastapi import FastAPI
from api.sessions import router as sessions_router
from api.gameplay import router as gameplay_router
from api.save_load import router as save_load_router
from api.metadata import router as metadata_router

app = FastAPI(title="Jericho Z-Machine API")

app.include_router(sessions_router)
app.include_router(gameplay_router)
app.include_router(save_load_router)
app.include_router(metadata_router)
