from abc import ABC, abstractmethod
from copy import copy
from typing import List

from srai_core.model.encoder_header import EncoderHeader
from srai_core.model.encoding import Encoding


class EncoderBase(ABC):

    def __init__(self, encoder_header: EncoderHeader):
        self.encoder_header = encoder_header

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass

    @property
    def list_accepted_content_type(self) -> List[str]:
        return copy(self.encoder_header.list_accepted_content_type)

    @abstractmethod
    def encode(self, instance_bytes: bytes) -> Encoding:
        raise NotImplementedError()
