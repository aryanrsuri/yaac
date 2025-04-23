from ulid import ulid
from datetime import datetime
class Deck:
    ulid: str
    label: str
    created_at: str = datetime.now().isoformat()

    def __init__(self, label: str):
        self.ulid = ulid()
        self.label = label
    
    def to_dict(self):
        return {
            "ulid": self.ulid,
            "label": self.label,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        deck = cls(data["label"])
        deck.ulid = data["ulid"]
        deck.created_at = data["created_at"]
        return deck
