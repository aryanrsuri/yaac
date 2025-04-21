from ulid import ulid
class Deck:
    ulid: str
    label: str
    def __init__(self, label: str):
        self.ulid = ulid()
        self.label = label
