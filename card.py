from ulid import ulid
from enum import Enum

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
    queue: Queue = Queue.New
    rep: int = 0
    interval: int = 1
    ease: float = 2.5

    def __init__(self, q: str, a: str):
        self.ulid = ulid()
        self.question = q
        self.answer = a

    def __repr__(self):
        buffer = ""
        if self.question:
            buffer += " Question: %s" % self.question
        else:
            buffer += self.ulid
        return buffer

    def add(self, deck_ulid: str):
        self.deck_ulid = deck_ulid

    def cycle(self, quality: int):
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
        
