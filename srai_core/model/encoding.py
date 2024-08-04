import hashlib
from typing import List

from pydantic import BaseModel


class Encoding(BaseModel):
    encoding_id: str
    instance_id: str
    encoder_id: str
    created_at_posix_timestamp: int
    list_metadata: List[dict]
    list_encoding: List[List[float]]

    @staticmethod
    def create_encoding_id(instance_id: str, encoder_id: str):
        return hashlib.sha256(f"{instance_id}-{encoder_id}".encode()).hexdigest()
