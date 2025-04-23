import os
import json
from ulid import ulid
from tag import Tag, TagType
from card import Card
from deck import Deck
from datetime import datetime

root: str = ".yaac/"
class Collection:
    ulid: str
    label: str
    version: int = 1
    saturation: int = 10
    decks: dict[str, Deck] = {}
    cards: dict[str, Card] = {}
    tags: dict[str, Tag] = {}
    created_at: str = datetime.now().isoformat()

    def __init__(self, label: str):
        self.ulid = ulid()
        if len(label) >= 3:
            self.label = label
        else:
            raise ValueError("Label too short (must be 3 or more characters).")

    def __repr__(self):
        buffer = "%s\t%s\n" % (self.ulid, self.label)
        buffer += str(list(self.decks.keys()))+"\n"
        for card in self.cards.values():
            buffer += card.__repr__() + "\n"
        return buffer

    def __partition__(self) -> str:
        p_1: str = self.ulid[:2] + "/"
        p_2: str = self.ulid[2:4] + "/"
        if not os.path.exists(root+p_1):
            os.makedirs(root+p_1)
        if not os.path.exists(root+p_1+p_2):
            os.makedirs(root+p_1+p_2)
        return root+p_1+p_2

    def purge(self):
        confirm = input("Are you sure you want to delete collection %s? Enter the collection label to confirm: " % self.ulid)
        if confirm == self.label:
            os.remove(self.__partition__()+self.ulid+".json")
        else:
            print("Sorry, this label is not correct")

    
    def write(self):
        data = {
            "ulid": self.ulid,
            "label": self.label,
            "version": self.version,
            "saturation": self.saturation,
            "created_at": self.created_at,
            "decks": [deck.to_dict() for deck in self.decks.values()],
            "cards": [card.to_dict() for card in self.cards.values()],
            "tags": [tag.to_dict() for tag in self.tags.values()]
        }

        with open(self.__partition__()+self.ulid+".json", "w") as f:
            json.dump(data, f, indent=2)

    def read(self):
        with open(self.__partition__()+self.ulid+".json", "r") as f:
            data = json.load(f)

        self.ulid = data["ulid"]
        self.label = data["label"]
        self.saturation = data.get("saturation", 10)
        self.version = data["version"]
        self.created_at = data["created_at"]

        self.decks = {}
        for d in data.get("decks", []):
            deck = Deck.from_dict(d)
            self.decks[deck.ulid] = deck

        self.cards = {}
        for c in data.get("cards", []):
            card = Card.from_dict(c)
            self.cards[card.ulid] = card
        
        self.tags = {}
        for t in data.get("tags", []):
            tag = Tag.from_dict(t)
            self.tags[tag.ulid] = tag

    def create_tag(self, label: str, tag_type: TagType = TagType.Label, description: str = ""):
        t = Tag(label, tag_type, description)
        self.tags[t.ulid] = t
        return t.ulid
   
    def create_card(self, q: str, a: str) -> str:
        c = Card(q, a)
        self.cards[c.ulid] = c
        return c.ulid

    def create_deck(self, label: str) -> str:
        d = Deck(label)
        self.decks[d.ulid] = d
        return d.ulid

    def add_card_to_deck(self, card_ulid: str, deck_ulid: str):
        card: Card = self.cards[card_ulid]
        card.add(deck_ulid)
   
    def add_tag_to_card(self, tag_ulid: str, card_ulid: [str] ):
        tag: Tag = self.tags[tag_ulid]
        tag.add(card_ulid)

    def remove_card_from_deck(self, card_ulid: str, deck_ulid: str):
        # TODO: Implement this using card.remove(...)
        raise NotImplemented
    
    def remove_tag_from_card(self, tag_ulid: str, card_ulid: str):
        tag: Tag = self.tags[tag_ulid]
        tag.remove(card_ulid)

    def remove_deck(self, deck_ulid: str) -> str:
        del self.decks[deck_ulid]

    def remove_card(self, card_ulid: str) -> str:
        del self.cards[card_ulid]
    
    def remove_tag(self, tag_ulid: str) -> str:
        del self.tags[tag_ulid]


    

    def cycle(self, deck_ulid: str):
        queue = self.build(deck_ulid)
        for i, (_, card) in enumerate(queue[:self.saturation]):
            print(f"\nQuestion: {card.question}")
            show = input("Show answer? (y/n): ").strip().lower()
            if show == "y":
                print(f"Answer: {card.answer}")
            
            while True:
                try:
                    quality = int(input("How well did you recall it? (0–5): "))
                    if 0 <= quality <= 5:
                        break
                    else:
                        print("Please enter a number from 0 to 5.")
                except ValueError:
                    print("Please enter an integer.")

            card.cycle(quality)

    def build(self, deck_ulid: str) -> list[tuple[int, Card]]:
        deck = self.decks.get(deck_ulid)
        if not deck:
            raise KeyError("Deck not found")

        due_cards = [
            (card.queue.value, card)
            for card in self.cards.values()
            if card.deck_ulid == deck.ulid 
            and card.queue != Queue.Archived
            and card.is_due()
        ]

        return due_cards.sort(key=lambda c: c[0])
                

            
