yaac (yet another anki clone):
CLI tool for studying flashcards with a SM-2 based spaced repition algorithm.
Cards will be queued based on the SM-2 and saturation of studying

Structure
```
Collection
|_ Deck(s)
|_ Card(s) [Assigned to Decks]
|_ Tag(s)  [Assigned to Cards]
```

SM-2 Algorithm
```python
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
```