from datetime import datetime
from ulid import ulid
from enum import Enum


class TagType(int, Enum):
    Label = 0
    Difficulty = 1
    Status = 2
    Flag = 3


class Tag:
    ulid: str
    label: str
    tag_type: TagType
    description: str
    created_at: str
    cards: list[str]

    def __init__(self, label: str, tag_type: TagType, description: str):
        self.ulid = ulid()
        self.label = label
        self.tag_type = tag_type
        self.description = description
        self.cards = []
        self.created_at = datetime.now().isoformat()

    def __repr__(self) -> str:
        return f"{self.label} ({len(self.cards)} cards)"

    def add(self, card_ulid: [str]):
        self.cards.extend(card_ulid)

    def remove(self, card_ulid: str):
        self.cards.remove(card_ulid)

    def to_dict(self) -> dict:
        return {
            "ulid": self.ulid,
            "label": self.label,
            "description": self.description,
            "tag_type": self.tag_type.value,
            "cards": self.cards,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        tag = cls(
            data["label"],
            TagType(data["tag_type"]),
            data["description"]
        )
        tag.ulid = data["ulid"]
        tag.cards = data["cards"]
        tag.created_at = data["created_at"]
        return tag
