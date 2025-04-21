import json
from ulid import ulid
from card import Card
from deck import Deck
class Collection:
    ulid: str
    label: str
    saturation: int = 10
    decks: dict[str, Deck] = {}
    cards: dict[str, Card] = {}

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

    def write(self):
        serial = {}
        serial["ulid"] = self.ulid
        serial["label"] = self.label
        serial["saturation"] = self.saturation
        if len(self.decks) > 0:
            serial["decks"] = [{deck.ulid: deck.__dict__} for deck in self.decks.values()]
        if len(self.cards) > 0:
            serial["cards"] = [{card.ulid: card.__dict__} for card in self.cards.values()]
        with open("yaac.json", "w") as f:
            #f.write(json.dumps(serial))
            f.write(json.dumps(self.__dict__))

    def read(self):
        with open("yaac.json", "r") as f:
            collection = json.load(f)
        self.ulid = collection["ulid"]
        self.label = collection["label"]
        self.saturation = collection["saturation"]
        self.decks = collection["decks"]
        self.cards = collection["cards"]
    
    def create_deck(self, label: str) -> str:
        d = Deck(label)
        self.decks[d.ulid] = d
        return d.ulid

    def create_card(self, q: str, a: str) -> str:
        c = Card(q, a)
        self.cards[c.ulid] = c
        return c.ulid

    def add_card_to_deck(self, card_ulid: str, deck_ulid: str):
        card: Card = self.cards[card_ulid]
        card.add(deck_ulid)

    def cycle(self, queue: list):
        for i, (_, card) in enumerate(queue):
            if i == self.saturation:
                break
            print(card.question)
            space = input("Show answer? (y/n): ")
            if space == "y":
                print(card.answer)
            quality = input("How well did you recover the information? Answer 0-5: ")
            if int(quality) not in {0, 1, 2, 3, 4, 5}:
                raise ValueError("Quality not integer between 0 and 5")
        card.cycle(int(quality))


    def build(self, ulid: str) -> set[Card]:
        deck: Deck = self.decks[ulid]
        if deck is None:
            raise KeyError
        order = []
        for card in self.cards.values():
            if card.deck_ulid == deck.ulid:
                order.append((card.queue.value, card))
        return sorted(order, key=lambda c: c[0])
    


            
if __name__ == "__main__":
    collection = Collection("Mathematics")
    # deck_ulid = collection.create_deck("Logic")
    # card_ulid = collection.create_card("What is a deductive arguement", "One where if the premise(s) are assumed to be true, the conclusion is impossible to be false.")
    # card_ulid_2 = collection.create_card("What is a inductive arguement", "One where if the premise(s) are assumed to be true, the conclusion is probably true.")
    # collection.add_card_to_deck(card_ulid, deck_ulid)
    # collection.add_card_to_deck(card_ulid_2, deck_ulid)

    # queue = collection.build(deck_ulid)
    # collection.cycle(queue)

    collection.read()
    collection.write()

    print(collection.__dict__)






            
