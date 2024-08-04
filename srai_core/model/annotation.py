import hashlib
from typing import List

from pydantic import BaseModel


class Annotation(BaseModel):
    annotation_id: str
    instance_id: str
    list_encoding_id: List[str]

    created_at_posix_timestamp: int
    metadata: dict

    @staticmethod
    def create_annotation_id(decoder_id: str, list_encoder_id: List[str]):
        code = decoder_id
        for encoder_id in list_encoder_id:
            code += encoder_id
        return hashlib.sha256(code.encode()).hexdigest()
