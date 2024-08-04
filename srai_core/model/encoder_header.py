from typing import List

from pydantic import BaseModel


class EncoderHeader(BaseModel):
    encoder_id: str
    encoder_name: str
    list_accepted_content_type: List[str]
    created_at_posix_timestamp: int
    dimension: int
    metadata: dict
