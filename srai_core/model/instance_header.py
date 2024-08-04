from pydantic import BaseModel

LIST_CONTENT_TYPES = ["text/plain", "image/jpeg", "video/mp4", "audio/mpeg"]


class InstanceHeader(BaseModel):
    instance_id: str
    content_type: str
    content_size: int
    created_at_posix_timestamp: int
    metadata: dict
