from pydantic import BaseModel
from typing import Tuple

class OpensearchConfiguration(BaseModel):
    
    class NetworkConfig(BaseModel):
        host_ip : str
        host_port: int
        def __init__(self):
            self.host_ip: str = "0.0.0.0"
            self.host_port: int = 9200

    class UserConfig(BaseModel):
        auth_info: Tuple[str, str]
        def __init__(self):
            self.auth_info = ("admin", "Xcaliber#7#",)

    network_config: NetworkConfig
    user_config: UserConfig

    def __init__(self):
       self.network_config = self.NetworkConfig()
       self.user_config = self.UserConfig()


