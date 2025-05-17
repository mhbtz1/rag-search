from pydantic import BaseModel
from typing import Tuple, Optional

class OpensearchConfiguration(BaseModel):
    class NetworkConfig(BaseModel):
        host_ip : Optional[str]=None
        host_port: Optional[int]=None
        def __init__(self):
            super().__init__()
            self.host_ip: str = "0.0.0.0"
            self.host_port: int = 9200


    class UserConfig(BaseModel):
        auth_info: Optional[Tuple[str, str]]=None
        def __init__(self):
            super().__init__()
            self.auth_info = ("admin", "Xcaliber#7#",)

    network_config: Optional[NetworkConfig]=None
    user_config: Optional[UserConfig]=None

    def __init__(self):
       super().__init__()
       self.network_config = self.NetworkConfig()
       self.user_config = self.UserConfig()


