import io
import os
from minio import Minio
from minio.error import S3Error
from osearch.cluster import OSExecutor
from utils.log import logger


def upload_image(bucket_name: str, image_bytes: io.BytesIO, object_name: str):
    try:
        logger.info(f"Uploading image...")
        client = Minio(
            f"{os.environ['MINIO_HOST']}:{os.environ['MINIO_PORT']}",
            access_key="admin",  
            secret_key="Xcaliber#7#", 
            secure=False
        )

        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created.")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists.")

        
        logger.info(f"First 512 image bytes: {image_bytes.read(512)}")
        image_bytes.seek(0)
        client.put_object(bucket_name=bucket_name, object_name=object_name, data=image_bytes, length=image_bytes.getbuffer().nbytes, content_type="image/jpeg")
        logger.info(f"Image '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

    except S3Error as err:
        print(f"An error occurred: {err}")
