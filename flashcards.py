import json
import random
import os

class FlashcardProgram:
    
    @staticmethod
    def get_available_subjects():
        """Skenira 'data/' mapu i vraća listu dostupnih predmeta."""
        subject_files = []
        data_dir = 'data'
        try:
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    subject_name = os.path.splitext(filename)[0].capitalize()
                    subject_files.append((subject_name, filename))
            return subject_files
        except FileNotFoundError:
            return []

    def __init__(self, filename):
        self.filename = os.path.join('data', filename)
        self.cards = self._load_cards()
        self.session_cards = []
        self.total_in_session = 0
        self.current_session_index = 0
        self.incorrect_cards_list = []
        self.current_card = None

    def _load_cards(self):
        """Učitava kartice iz JSON fajla."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def get_subject_name(self):
        """Vraća naziv predmeta na osnovu imena fajla."""
        base_name = os.path.basename(self.filename)
        return os.path.splitext(base_name)[0].capitalize()


    def start_session(self):
        """Pokreće novu sesiju učenja."""
        if not self.cards:
            return

        self.session_cards = self.cards.copy()
        random.shuffle(self.session_cards)
        
        self.total_in_session = len(self.session_cards)
        self.current_session_index = 0
        self.incorrect_cards_list = []
        self.current_card = None

    def get_next_card_in_session(self):
        """Vraća sljedeću karticu u izmiješanoj sesiji."""
        if not self.session_cards:
            self.current_card = None
            return None, "Sesija završena!"

        self.current_session_index += 1
        self.current_card = self.session_cards.pop()
        
        progress_text = f"Pitanje: {self.current_session_index} / {self.total_in_session}"
        
        return self.current_card.get('naslov', 'Nema naslova'), progress_text

    def get_current_answer(self):
        """Vraća puni odgovor za trenutno izabranu karticu."""
        if self.current_card:
            return self.current_card.get('puni_odgovor', 'Nema odgovora')
        return "Nema odgovora."

    def mark_current_incorrect(self):
        """Ne znam odgovor."""
        if self.current_card and self.current_card not in self.incorrect_cards_list:
            self.incorrect_cards_list.append(self.current_card)

    def get_incorrect_summary(self):
        """Vraća listu naslova od pitanja na koja niste znali odgovor."""
        if not self.incorrect_cards_list:
            return "Sva pitanja ste znali! Čestitamo!"
        
        titles = [card.get('naslov', 'Nepoznato') for card in self.incorrect_cards_list]
        return "Pitanja koja niste znali:\n- " + "\n- ".join(titles)