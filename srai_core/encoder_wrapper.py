from abc import ABC, abstractmethod
from copy import copy
from typing import List

from srai_core.encoder_base import EncoderBase
from srai_core.model.encoding import Encoding
from srai_core.model.instance_header import InstanceHeader
from srai_core.store.bytes_store_base import BytesStoreBase
from srai_core.store.document_store_base import DocumentStoreBase


class EncoderWapper(ABC):

    def __init__(
        self,
        encoder: EncoderBase,
        instance_header_store: DocumentStoreBase,
        instance_store: BytesStoreBase,
        encoding_store: DocumentStoreBase,
    ):
        self.encoder = encoder
        self.encoder.load()
        self.instance_header_store = instance_header_store
        self.instance_store = instance_store
        self.encoding_store = encoding_store

    @property
    def encoder_id(self):
        return self.encoder.encoder_header.encoder_id

    @property
    def list_accepted_content_type(self) -> List[str]:
        return copy(self.encoder.list_accepted_content_type)

    @abstractmethod
    def encode(self, instance_id: str) -> Encoding:
        encoding_id = Encoding.create_encoding_id(
            instance_id=instance_id, encoder_id=self.encoder.encoder_header.encoder_id
        )
        document = self.encoding_store.try_load_document(encoding_id)
        if document is not None:
            return Encoding(**document)
        instance_header = InstanceHeader(**self.instance_header_store.load_document(instance_id))
        if instance_header.content_type not in self.list_accepted_content_type:
            raise ValueError(
                f"Encoder {self.encoder.encoder_header.encoder_id} is not allowed for instance {instance_id}"
            )
        instance_bytes = self.instance_store.load_bytes(instance_id)
        encoding = self.encoder.encode(instance_bytes)
        self.encoding_store.save_document(encoding_id, encoding.model_dump())
        return encoding
