from fastapi import FastAPI, APIRouter, Depends, status, Request, HTTPException
from fastapi import UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import psycopg2


app = FastAPI()
router = APIRouter()
security = HTTPBearer()

app.include_router(router, prefix="/search-api")

def fetch_secret_token(username: str):
    connection = psycopg2.connect({
        
    })


def verify_token(username: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != fetch_secret_token(username):
         raise HTTPException(f"Login not valid for username {username}!")
    return token

@router.post("/sift_documents")
async def sift_documents(request: Request):
    pass


@router.get("/available_indices")
async def available_indices(request: Request):
    pass


@router.post("/ingest_file")
async def ingest_file(request: Request, file: UploadFile):
    pass


@router.post("/ingest_files")
async def batch_ingest_files(request: Request):
    pass



