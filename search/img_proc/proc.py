import io
import uuid
import numpy
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from osearch.cluster import OSExecutor
from typing import Optional

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
        embedding = outputs.detach().numpy()
        return embedding

    def index_image_embedding(self, model_alias: str, image_path: Optional[str]=None, image_content: Optional[io.BytesIO]=None, caption_text: Optional[str]=None, index: str = "large-image-embedding-index"):
        if not (image_path or image_content):
            raise Exception("Both image_path and image_content are null!")
        
        try:
            if not caption_text:
                caption_text = ""

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
                            "dim": 512
                        },
                        "image_id": {"type": "keyword"},
                        "caption": {"type": "text"}
                    }
                }
            }

            if not self.os_executor.exists_index(index=index):
                self.os_executor.create_index(index=index, mapping=mapping)

            embedding = self.process_image(image_path=image_path, image_content=image_content)
            image_id = str(uuid.uuid4())
            self.os_executor.update_index(index=index, id=image_id, body = {"image_vector": embedding.tolist(), "image_id": image_id, "caption": caption_text})
        except Exception as e:
            raise e
        