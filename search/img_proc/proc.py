import io
import uuid
import numpy
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from osearch.cluster import OSExecutor
from typing import Optional
from utils.log import logger
from img_proc.minio import upload_image

class ImageProcessor:
    def __init__(self):
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.os_executor = OSExecutor()

    def process_image(self, image_path: Optional[str]=None, image_content: Optional[io.BytesIO]=None) -> numpy.ndarray:
        if not (image_path or image_content):
            raise Exception("Both image_path and image_content are null!")
        
        if image_path:
            img = Image.open(image_path, mode='r')
        else:
            img = Image.open(fp=image_content, mode='r')

        inputs = self.processor(images=img, return_tensors="pt")
        outputs = self.model.get_image_features(**inputs)
        embedding = outputs.detach().numpy().squeeze(axis=0)
        return embedding

    def index_image_embedding(self, model_alias: str,  image_bytes: io.BytesIO, image_path: Optional[str]=None, image_content: Optional[numpy.ndarray]=None, caption_text: Optional[str]=None, index: str = "large-image-embedding-index"):
        logger.info(f"Running index_image_embedding on model alias {model_alias}")
        if (image_path is None) and (image_content is None):
            logger.info("Both image_path and image_content are null!")
            raise Exception("Both image_path and image_content are null!")
        
        try:
            if not caption_text:
                caption_text = ""

            logger.info(f"Point 1")
            mapping = {
                "settings": {
                    "index": {
                        "knn": True
                    }
                },
                "mappings": {
                    "properties": {
                        "image_vector": {
                            "type": "knn_vector",
                            "dimension": 512,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib"
                            }
                        },
                        "image_id": {"type": "keyword"},
                        "caption": {"type": "text"},
                        "minio_image_id": {"type": "keyword"}
                    }
                }
            }
            logger.info(f"Point 2")
            if not self.os_executor.exists_index(index=index):
                self.os_executor.create_index(index=index, mapping=mapping)

            obj_name = str(uuid.uuid4())
            logger.info(f"First 512 bytes: {image_bytes.read(512)}")
            image_bytes.seek(0)
            upload_image(bucket_name="imgbucket", object_name=obj_name, image_bytes=image_bytes)
            logger.info(f"Point 3")
            minio_image_id=f"imgbucket_{obj_name}"
            logger.info(f"minio_image_id: {minio_image_id}")
            self.os_executor.update_index(index=index, document_id=obj_name, body = {"image_vector": image_content.tolist(), "image_id": obj_name, "caption": caption_text, "minio_image_id": minio_image_id})
            logger.info(f"Point 4")

        except Exception as e:
            raise e
        