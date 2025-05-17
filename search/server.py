from fastapi import FastAPI, APIRouter, Request, Response, Body, HTTPException
from fastapi import UploadFile
from fastapi.responses import JSONResponse 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Dict, Optional
from osearch.cluster import OSExecutor
from .config import ServerConfiguration
import logging
import secrets
import psycopg2

logger = logging.getLogger("server-log")
fh = logging.FileHandler(filename="server-log.log", mode="a")
fh.setLevel(logging.INFO)
logger.addHandler(fh)
logger.setLevel(logging.INFO)

prefix = "/search_api"
app = FastAPI(title="Multimodal Search Application",
              docs_url=f"{prefix}/docs")

router = APIRouter(prefix=prefix)
security = HTTPBearer()

async def fetch_secret_token(dbconfig: Dict[str, str], username: str, password: str) -> Optional[str]:
    conn = psycopg2.connect(
        dbname=dbconfig["dbname"],
        user="postgres",
        password="postgres",
        host=dbconfig["host"],
        port=dbconfig["port"]
    )


    with conn.cursor() as cursor:
        all_tables = cursor.execute("""
           SELECT table_name from information_schema.tables
           WHERE table_schema = 'public'
        """)
        all_tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"all tables: {all_tables}")
        if "users" not in all_tables:
            logger.info("users table not found. Creating table...")
            cursor.execute("CREATE TABLE users (username VARCHAR, password VARCHAR, token VARCHAR)")
            conn.commit()
        
        cursor.execute(f"SELECT password, token FROM users WHERE username = '{username}'")
        results = cursor.fetchall()
        if len(results) == 0:
            token = secrets.token_hex(64)
            cursor.execute(f"INSERT INTO users (username, password, token) VALUES ('{username}', '{password}', '{token}')")
            conn.commit()
            return token
        else:
            pot_password, token = results[0][0], results[0][1]
            if pot_password == password:
                return token
        
    
    return None


@router.post("/login")
async def login(username: Annotated[str, Body()], password: Annotated[str, Body()]):
    dbconfig = {
        "user": username,
        "password": password,
        "dbname": ServerConfiguration().DATABASES[0]["dbname"],
        "host": ServerConfiguration().DATABASES[0]["dbhost"],
        "port": ServerConfiguration().DATABASES[0]["dbport"]
    }
    result = await fetch_secret_token(dbconfig=dbconfig, username=username, password=password)
    if result:
        logger.info(f"result: {result}")
        return JSONResponse(content={"token": result}, status_code=200, headers={"Content-Type": "application/json"})
    return JSONResponse(content={"status": "error"}, status_code=400, headers={"Content-Type": "application/json"})


@router.post("/items/{item_id}")
async def test_point(item_id: int, value_one: int = 0, value_two: int = 10):
    return Response(content={"sum": item_id + value_one + value_two}, headers={"Content-Type": "application/json"}, status_code=200)


@router.post("/sift_documents")
async def sift_documents(request: Request):
    availab


@router.get("/available_indices", dependencies=[])
async def available_indices(request: Request):
    try:
        os_executor = OSExecutor()


@router.post("/ingest_file")
async def ingest_file(request: Request, file: UploadFile):
    pass


@router.post("/ingest_files")
async def batch_ingest_files(request: Request):
    pass


app.include_router(router)
