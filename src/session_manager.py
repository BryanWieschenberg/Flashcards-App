import csv
import json
import random
import os

SESSION_FILE = "session.json"
TERMS_FILE = "cards.csv"

class SessionManager:
    def __init__(self):
        self.all_cards = self.load_cards()
        self.cards = list(self.all_cards.items())
        self.shuffle_enabled = False
        self.show_term_first = True
        self.reset_state()

    def reset_state(self):
        self.current_index = 0
        self.needs_study = []
        self.mastered_indices = []

    def load_cards(self):
        cards = {}
        if not os.path.exists(TERMS_FILE):
            return {"Sample Term": "Sample Definition"}
            
        with open(TERMS_FILE, newline='', encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                next(reader)
                for row in reader:
                    if len(row) >= 2:
                        term, definition = row[0].strip(), row[1].strip()
                        cards[term] = definition
            except StopIteration:
                pass
        return cards

    def save_session(self):
        data = {
            "current_index": self.current_index,
            "mastered_indices": self.mastered_indices,
            "needs_study": self.needs_study,
            "shuffle_enabled": self.shuffle_enabled,
            "show_term_first": self.show_term_first,
            "cards": self.cards 
        }
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)

    def load_session(self):
        if not os.path.exists(SESSION_FILE):
            return False
            
        try:
            with open(SESSION_FILE, 'r') as f:
                data = json.load(f)
                self.current_index = data.get("current_index", 0)
                self.mastered_indices = data.get("mastered_indices", [])
                self.needs_study = [tuple(card) for card in data.get("needs_study", [])]
                self.shuffle_enabled = data.get("shuffle_enabled", False)
                self.show_term_first = data.get("show_term_first", True)
                self.cards = [tuple(card) for card in data.get("cards", self.cards)]
            return True
        except:
            return False

    def clear_session(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.reset_state()
        self.cards = list(self.all_cards.items())
        if self.shuffle_enabled:
            random.shuffle(self.cards)

    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled
        if self.shuffle_enabled:
            random.shuffle(self.cards)
        else:
            self.cards = list(self.all_cards.items())

    def mark_mastered(self, index):
        if index not in self.mastered_indices:
            self.mastered_indices.append(index)
        
        card = self.cards[index]
        if card in self.needs_study:
            self.needs_study.remove(card)

    def mark_needs_study(self, index):
        card = self.cards[index]
        if card not in self.needs_study:
            self.needs_study.append(card)
        
        if index in self.mastered_indices:
            self.mastered_indices.remove(index)

    def undo_action(self, index):
        if self.needs_study and self.needs_study[-1] == self.cards[index]:
            self.needs_study.pop()
        
        if index in self.mastered_indices:
            self.mastered_indices.remove(index)

    def is_complete(self):
        return self.current_index >= len(self.cards)

    def get_next_loop(self):
        if self.needs_study:
            self.cards = list(self.needs_study)
            self.needs_study = []
            self.mastered_indices = []
            self.current_index = 0
            return True
        return False
