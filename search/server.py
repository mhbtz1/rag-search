import io
import json
import asyncio
import uuid
from fastapi import FastAPI, APIRouter, Request, Response, Body, Form, HTTPException, Depends, File
from fastapi import UploadFile
from fastapi.responses import JSONResponse 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Dict, List, Optional
from osearch.cluster import OSExecutor
from ingestors.ingestor import PDFIngestor, DocxIngestor, CSVIngestor
from utils.conn import spawn_connection
from configurations.models import SearchParams

from config import ServerConfiguration
from fastapi.middleware.cors import CORSMiddleware
from engine import Retriever, ImageRetriever
from utils.log import logger
from img_proc.proc import ImageProcessor
import secrets
import psycopg2



prefix = "/retr"
app = FastAPI(title="Multimodal Search Application",
              docs_url=f"{prefix}/docs")

router = APIRouter(prefix=prefix)
security = HTTPBearer()
retriever = Retriever()
image_retriever = ImageRetriever()


async def fetch_secret_token(dbconfig: Dict[str, str], username: str, password: str) -> Optional[str]:
    conn = spawn_connection()

    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS accounts (username VARCHAR, password VARCHAR, token VARCHAR)")
        conn.commit()
        cursor.execute("SELECT password, token FROM accounts WHERE username = %s", (username,))
        results = cursor.fetchall()
        if len(results) == 0:
            token = secrets.token_hex(64)
            cursor.execute("INSERT INTO accounts (username, password, token) VALUES (%s, %s, %s)", (username, password, token,))
            conn.commit()
            return token
        else:
            pot_password, token = results[0][0], results[0][1]
            if pot_password == password:
                return token
        
    
    return None

@router.post("/register")
async def register(username: Annotated[str, Body()], password: Annotated[str, Body()]):
    try:
        conn = spawn_connection()
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS accounts (username VARCHAR, password VARCHAR, token VARCHAR)")
            conn.commit()
            token = str(uuid.uuid4())
            cursor.execute("INSERT INTO accounts (username, password, token) VALUES (%s, %s, %s)", (username, password, token,))
            conn.commit()
        return JSONResponse(content={"token": token}, status_code=200, headers={"Content-Type": "application/json"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400, headers={"Content-Type": "application/json"})


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
async def test_point(item_id: int, value_one: Annotated[int, Body()] = 0, value_two: Annotated[int, Body()] = 10):
    return JSONResponse(content={"sum": item_id + value_one + value_two}, headers={"Content-Type": "application/json"}, status_code=200)


@router.post("/sift_documents")
async def sift_documents(request: Request):
    pass

@router.get("/available_indices", dependencies=[])
async def available_indices(request: Request):
    try:
        os_executor = OSExecutor()
        return JSONResponse(content={"indices": os_executor.list_available_indices()}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

async def process_single_file(request: Request, model_params: str = Form(...), file: UploadFile = File(description="File to ingest further into backend", example="document.pdf")):
    try:
        doc_type = ""
        conn = spawn_connection()
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS fstatus (filename VARCHAR, status VARCHAR)")
        conn.commit()
        cursor.execute("CREATE TABLE IF NOT EXISTS id_map (id INTEGER, filename VARCHAR)")
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM id_map")
        file_id = cursor.fetchall()[0][0]
        enhanced_fname = f"{file.filename}-{file_id}"

        cursor.execute("INSERT INTO id_map (id, filename) VALUES (%s, %s)", (file_id, file.filename,))
        conn.commit()
        cursor.execute("INSERT INTO fstatus (filename, status) VALUES (%s, %s)", (enhanced_fname, "PENDING",))

        if file.filename.endswith(".pdf"):
            doc_type = "pdf"
            ingestor = PDFIngestor()
        elif file.filename.endswith(".csv") or file.filename.endswith(".xlsx"):
            doc_type = "relational"
            ingestor = CSVIngestor()
        elif file.filename.endswith(".docx"):
            doc_type = "docx"
            ingestor = DocxIngestor()
        else:
            return JSONResponse(content={"error": f"File not supported: {file.filename}"}, status_code=400)
        
        content = file.file.read()
        bytes_io = io.BytesIO(content)
        parsed_content = ingestor.parse(document_content=bytes_io, strategy='hi_res')
        bytes_io = io.BytesIO(content)

        cursor.execute("UPDATE fstatus SET status = 'PARSED' WHERE filename = %s", (enhanced_fname,))
        conn.commit()

        index = f"{model_params}-embedding-index"
        ingestor.embed(index=index, model_alias=model_params, document_content=parsed_content)

        cursor.execute("UPDATE fstatus SET status = 'FINISHED' WHERE filename = %s", (enhanced_fname,))
        conn.commit()
        return JSONResponse(content={"status": "success"}, status_code=200)
  
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

async def process_single_image(request: Request, model_params: str = Form(...), image_file: UploadFile = File(...)):
    try:
        logger.info(f"Processing file {image_file.filename} with model alias {model_params}...")
        conn = spawn_connection()
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS fstatus (filename VARCHAR, status VARCHAR)")
        conn.commit()
        cursor.execute("CREATE TABLE IF NOT EXISTS id_map (id INTEGER, filename VARCHAR)")
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM id_map")
        file_id = cursor.fetchall()[0][0]
        enhanced_fname = f"{image_file.filename}-{file_id}"

        cursor.execute("INSERT INTO id_map (id, filename) VALUES (%s, %s)", (file_id, image_file.filename,))
        conn.commit()
        cursor.execute("INSERT INTO fstatus (filename, status) VALUES (%s, %s)", (enhanced_fname, "PENDING",))

        ingestor = ImageProcessor()

        content = image_file.file.read()
        bytes_io = io.BytesIO(content)
        parsed_content = ingestor.process_image(image_content=bytes_io)
        bytes_io = io.BytesIO(content)

        cursor.execute("UPDATE fstatus SET status = 'PARSED' WHERE filename = %s", (enhanced_fname,))
        conn.commit()
        '''
        logger.info(f"[process_image] embedding: {parsed_content}")
        logger.info(f"[process_image] embedding type: {type(parsed_content)}")
        logger.info(f"[process_image] embedding dim: {parsed_content.shape}")
        '''
        index = f"{model_params}-image-embedding-index"
        ingestor.index_image_embedding(index=index, model_alias=model_params, image_content=parsed_content, image_bytes=bytes_io)

        cursor.execute("UPDATE fstatus SET status = 'FINISHED' WHERE filename = %s", (enhanced_fname,))
        conn.commit()
        return JSONResponse(content={"status": "success"}, status_code=200)
  
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)


@router.get("/file_status/{id}")
async def get_status(id: int):
    conn = spawn_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT filename FROM id_map WHERE id = %s", (id,))
            filename = cursor.fetchall()[0][0]
            enhanced_fname = f"{filename}-{id}"
            cursor.execute("SELECT status FROM fstatus WHERE filename = %s", (enhanced_fname,))
            status = cursor.fetchall()[0][0]
            return JSONResponse(content={"status": status}, status_code=200)
    except Exception as e:
        return JSONResponse({"status": str(e)}, status_code=400)

@router.post("/ingest_image")
async def ingest_image(request: Request, model_params: str = Form(...), image_file: UploadFile = File(...)):
    try:
        response = await process_single_image(request=request, model_params=model_params, image_file=image_file)
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
@router.post("/ingest_file")
async def ingest_file(request: Request, model_params: str = Form(...), file: UploadFile = File(...)):
    try:
        response = await process_single_file(request=request, model_params=model_params, file=file)
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
        
@router.post("/ingest_files")
async def batch_ingest_files(request: Request, model_params: str = Form(...), files: List[UploadFile] = File(...)):
    try:
        await asyncio.gather(*[process_single_file(request=request, model_params=model_params, file=file) for file in files])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@router.post("/search")
async def multimodal_search(request: Request, search_params: SearchParams):
    try:
        logger.info(f"[multimodal_search] search_params: {str(search_params)}")
        logger.info("[multimodal_search] Fetching documents...")
        reranked_docs = retriever.rag_query(query=search_params.query, top_k=search_params.top_k, index=search_params.document_index)
        logger.info(f"[multimodal_search] Fetching images...")
        reranked_images = image_retriever.rag_query(query=search_params.query, top_k=search_params.top_k, index=search_params.image_index)
        return JSONResponse(content={"documents": reranked_docs, "images": reranked_images}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=['*'], allow_headers=["*"])
app.include_router(router)
