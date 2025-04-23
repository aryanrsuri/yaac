from ulid import ulid
from enum import Enum
from datetime import datetime, timedelta


class Queue(int, Enum):
    New = 0
    Learning = 1
    ReviewLow = 2
    ReviewHigh = 3
    Lapsed = 4
    Archived = -1


class Card:
    ulid: str
    deck_ulid: str
    question: str
    answer: str
    created_at: str = datetime.now().isoformat()
    reviewed_at: str = datetime.now().isoformat()
    queue: Queue
    rep: int = 0
    interval: int = 1
    ease: float = 2.5

    def __init__(self, question: str, answer: str):
        self.ulid = ulid()
        self.queue = Queue.New
        self.question = question
        self.answer = answer

    def __repr__(self):
        qstate = f"[{self.queue.name}]"
        buffer = f"{qstate} {self.question}" if self.question else self.ulid
        return buffer
        
    def is_due(self) -> bool:
        return datetime.now() >= datetime.fromisoformat(self.reviewed_at) + timedelta(days=self.interval)

    def to_dict(self):
        return {
            "ulid": self.ulid,
            "deck_ulid": self.deck_ulid,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "question": self.question,
            "answer": self.answer,
            "queue": self.queue.value,
            "rep": self.rep,
            "interval": self.interval,
            "ease": self.ease,
        }

    @classmethod
    def from_dict(cls, data):
        card = cls(data["question"], data["answer"])
        card.ulid = data["ulid"]
        card.deck_ulid = data.get("deck_ulid")
        card.created_at = data["created_at"]
        card.reviewed_at = data["reviewed_at"]
        card.queue = Queue(data["queue"])
        card.rep = data["rep"]
        card.interval = data["interval"]
        card.ease = data["ease"]
        return card

    def add(self, deck_ulid: str):
        self.deck_ulid = deck_ulid

    def cycle(self, quality: int):
        self.reviewed_at = datetime.now().isoformat()
        if quality < 3:
            self.rep = 0
            self.interval = 1
            self.change()
            return [self.interval, self.rep, self.ease]
        elif self.rep == 0:
            self.interval = 1
        elif self.rep == 1:
            self.interval = 6
        elif self.rep > 1:
            self.interval = self.interval * self.ease
        self.interval = round(self.interval)
        self.rep += 1
        self.ease = self.ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if self.ease < 1.3:
            self.ease = 1.3
        self.change()

    def change(self):
        if self.queue == Queue.New:
            self.queue = Queue.Learning
        if self.queue == Queue.Learning:
            if self.ease > 3:
                self.queue = Queue.ReviewHigh
            else:
                self.queue = Queue.ReviewLow
        if self.interval > 10:
            self.queue = Queue.Lapsed
