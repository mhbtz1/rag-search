from pydantic import BaseModel
from typing import List, Dict

class ServerConfiguration(BaseModel):
    DATABASES: List[Dict] = [ {"dbname": "postgres0", "dbhost": "0.0.0.0", "dbport": 5432} ]