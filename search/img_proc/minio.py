import io
from minio import Minio
from minio.error import S3Error
from osearch.cluster import OSExecutor
from utils.log import logger

client = Minio(
    "localhost:9000",
    access_key="minioadmin",  
    secret_key="minioadmin", 
    secure=False
)

def upload_image(bucket_name: str, image_bytes: io.BytesIO, object_name: str):
    try:
        client = Minio(
            "localhost:9000",
            access_key="admin",  
            secret_key="Xcaliber#7#", 
            secure=False
        )

        os_executor = OSExecutor()

        # Check if the bucket exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")

        # Upload the image
        client.put_object(bucket_name=bucket_name, object_name=object_name, data=image_bytes, length=len(image_bytes), content="image/jpeg")
        logger.info(f"Image '{object_name}' uploaded successfully to bucket '{bucket_name}'.")

    except S3Error as err:
        print(f"An error occurred: {err}")
