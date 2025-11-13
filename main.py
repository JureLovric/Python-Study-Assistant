import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, scrolledtext, filedialog
from flashcards import FlashcardProgram
import json
import os
from PyPDF2 import PdfReader

from dotenv import load_dotenv

# Uvoz za Gemini API
try:
    from google import genai
    from google.genai.errors import APIError

    load_dotenv() 
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False


class StudijskiProgram(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Moj Studijski Asistent")
        self.geometry("700x500")
        
        self.current_subject_file = None
        self.flashcards = None

        if not os.path.exists('data'):
            os.makedirs('data')

        self.apply_modern_style()
        self.show_subject_selection_menu()

    def apply_modern_style(self):
        """Postavlja standardni stil za moderniji izgled."""
        
        self.option_add('*Font', 'Arial 10')
        
        self.default_bg = '#F0F0F0'
        self.button_color = '#4A86E8'
        self.text_color = '#333333'
        
        self.config(bg=self.default_bg)

        style = ttk.Style()
        style.theme_use('default')
        
        self.menu_button_style = {
            'font': ('Arial', 14, 'bold'),
            'bg': self.button_color,
            'fg': 'white',
            'activebackground': '#3C70D2',
            'relief': 'flat',
            'borderwidth': 0,
            'cursor': 'hand2',
            'padx': 15,
            'pady': 15
        }
        
        self.relief_style = {
            'bd': 1,
            'relief': 'groove', 
            'bg': 'white' 
        }

    # --- GLAVNI MENI ZA ODABIR PREDMETA ---
    def show_subject_selection_menu(self):
        """Prikazuje meni za odabir predmeta."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, 
                 text="Izaberite Predmet:", 
                 font=("Arial", 20, "bold"), 
                 bg=self.default_bg,
                 fg=self.text_color).pack(pady=30)
        
        subjects = FlashcardProgram.get_available_subjects()
        
        if not subjects:
            tk.Label(self, text="Nema dostupnih fajlova u 'data/' mapi.", fg="red", bg=self.default_bg).pack(pady=10)
            return

        for subject_name, filename in subjects:
            btn = tk.Button(self, 
                            text=f"» {subject_name} «", 
                            command=lambda f=filename: self.load_subject(f), 
                            width=30,
                            **self.menu_button_style)
            btn.pack(pady=8)
            
        tk.Button(self, text="Dodaj Novi Predmet/Fajl", 
                 command=self.add_new_subject, 
                 bg="lightgrey", fg=self.text_color, 
                 relief='flat', padx=10, pady=5).pack(pady=20)


    def load_subject(self, filename):
        """Učitava izabrani predmet i prelazi na glavni meni predmeta."""
        self.current_subject_file = filename
        self.flashcards = FlashcardProgram(filename)
        
        self.show_subject_options_menu()


    # --- GLAVNI MENI PREDMETA ---
    def show_subject_options_menu(self):
        """Prikazuje opcije za rad s izabranim predmetom."""
        for widget in self.winfo_children():
            widget.destroy()
            
        name = self.flashcards.get_subject_name()
        
        tk.Label(self, text=f"Predmet: {name}", font=("Arial", 24, "bold"), fg=self.button_color, bg=self.default_bg).pack(pady=20)
        
        main_option_style = {**self.menu_button_style, 'width': 45} 

        tk.Button(self, 
                  text="1. POKRENI FLASHCARDS (Sesija učenja)", 
                  command=self.show_flashcard_window, 
                  **main_option_style).pack(pady=8)
                  
        tk.Button(self, 
                  text="2. DODAJ NOVU KARTICU / BILJEŠKU", 
                  command=self.show_add_card_window, 
                  **main_option_style).pack(pady=8)

        tk.Button(self, 
                  text="3. BAZA SVIH PITANJA I PRETRAGA", 
                  command=self.show_question_database, 
                  **main_option_style).pack(pady=8)
                  
        tk.Button(self, 
                  text="4. POKRENI KVIZ/TESTIRANJE ZNANJA (AI)", 
                  command=self.show_quiz_setup_window, 
                **main_option_style).pack(pady=8)
        
        tk.Button(self, text="<< Nazad na Odabir Predmeta", 
                  command=self.show_subject_selection_menu, 
                  bg="#F0AD4E", fg=self.text_color, 
                  relief='flat', padx=10, pady=5).pack(pady=25)


    # --- FLASHCARDS LOGIKA I GUI ---

    def show_flashcard_window(self):
        """Kreira novi prozor za Flashcards sa praćenjem sesije."""
        
        if not self.flashcards.cards:
             messagebox.showerror("Greška", "Nema kartica za učenje. Dodajte ih prvo!")
             return
        
        self.flashcards.start_session()
        
        flash_window = tk.Toplevel(self, bg=self.default_bg)
        flash_window.title(f"Učenje - {self.flashcards.get_subject_name()}")
        flash_window.geometry("800x600")

        self.main_flashcard_frame = tk.Frame(flash_window, bg=self.default_bg)
        self.main_flashcard_frame = tk.Frame(flash_window)
        self.main_flashcard_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.progress_label = tk.Label(self.main_flashcard_frame, text="1/X", font=("Arial", 14, "italic"), fg="grey")
        self.progress_label.pack(anchor="ne", padx=10)

        tk.Label(self.main_flashcard_frame, text="Koncept / Pitanje:", font=("Arial", 10, "italic"), bg=self.default_bg).pack(pady=(10, 0))
        self.card_title_label = tk.Label(self.main_flashcard_frame, text="Pitanje...", font=("Arial", 18, "bold"), wraplength=750, bg=self.default_bg, fg=self.text_color)
        self.card_title_label.pack(pady=5)
        
        tk.Label(self.main_flashcard_frame, text="Odgovor / Bilješka:", font=("Arial", 10, "italic"), bg=self.default_bg).pack(pady=(10, 0))
        self.answer_label = tk.Label(self.main_flashcard_frame, text="", font=("Arial", 12), fg="blue", wraplength=750, justify=tk.LEFT, height=8, **self.relief_style)
        self.answer_label.pack(pady=5, padx=10, fill=tk.X)
        
        self.reveal_btn = tk.Button(self.main_flashcard_frame, text="KLIKNI I OTKRIJ ODGOVOR", command=self.reveal_answer, width=40, height=2, bg="lightcoral")
        self.reveal_btn.pack(pady=20)
        
        self.feedback_frame = tk.Frame(self.main_flashcard_frame)
        
        tk.Button(self.feedback_frame, text="NISAM ZNAO (Označi za ponavljanje)", 
                  command=lambda: self.handle_feedback(was_correct=False), 
                  width=30, height=2, bg="orange").pack(side=tk.LEFT, padx=10)
                  
        tk.Button(self.feedback_frame, text="ZNAO SAM (Sljedeća kartica)", 
                  command=lambda: self.handle_feedback(was_correct=True), 
                  width=30, height=2, bg="lightgreen").pack(side=tk.LEFT, padx=10)
        
        # Okvir za kraj sesije
        self.end_session_frame = tk.Frame(flash_window)
        tk.Label(self.end_session_frame, text="Sesija je završena!", font=("Arial", 20, "bold")).pack(pady=20)
        self.summary_text = scrolledtext.ScrolledText(self.end_session_frame, width=70, height=15, font=("Arial", 12))
        self.summary_text.pack(pady=10)
        tk.Button(self.end_session_frame, text="POKRENI PONOVO", 
                  command=lambda w=flash_window: self.restart_session(w), 
                  height=2, width=30, bg="lightblue").pack(pady=20)
        tk.Button(self.end_session_frame, text="Zatvori", 
                  command=flash_window.destroy, 
                  height=2, width=30, bg="lightgrey").pack()

        self.next_card()

    def next_card(self):
        """Postavlja sljedeću karticu u sesiji."""
        self.feedback_frame.pack_forget()
        self.reveal_btn.pack(pady=20)

        title, progress_text = self.flashcards.get_next_card_in_session()
        self.progress_label.config(text=progress_text)

        if title is None:
            self.end_session()
            return

        self.card_title_label.config(text=title)
        self.answer_label.config(text="[Klikni i otkrij odgovor...]")
        self.reveal_btn.config(state=tk.NORMAL)

    def reveal_answer(self):
        """Prikaz punog odgovora i dugmadi za feedback."""
        answer = self.flashcards.get_current_answer()
        self.answer_label.config(text=answer)
        self.reveal_btn.pack_forget()
        self.feedback_frame.pack(pady=20)

    def handle_feedback(self, was_correct):
        """Obrađuje feedback korisnika (znao / nije znao)."""
        if not was_correct:
            self.flashcards.mark_current_incorrect()
        self.next_card()

    def end_session(self):
        """Prikazuje ekran za kraj sesije."""
        self.main_flashcard_frame.pack_forget()
        summary = self.flashcards.get_incorrect_summary()
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
        self.end_session_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def restart_session(self, window):
        """Resetira GUI za početak nove sesije."""
        self.flashcards.start_session()
        self.end_session_frame.pack_forget()
        self.main_flashcard_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.next_card()
    
    # --- BAZA PITANJA I PRETRAGA ---
    def show_question_database(self):
        """Kreira prozor koji prikazuje listu svih pitanja s mogućnošću pregleda."""
        
        self.flashcards._load_cards()
        cards = self.flashcards.cards
        
        if not cards:
            messagebox.showinfo("Baza Pitanja", "Nema pitanja u bazi za ovaj predmet.")
            return

        db_window = tk.Toplevel(self)
        db_window.title(f"Baza Pitanja - {self.flashcards.get_subject_name()}")
        db_window.geometry("800x650")
        
        tk.Label(db_window, text="Pregled svih bilješki/pitanja", font=("Arial", 18, "bold")).pack(pady=10)
        
        main_frame = tk.Frame(db_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        left_frame = tk.Frame(main_frame, width=350)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="Lista pitanja:", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(left_frame, textvariable=search_var, width=40)
        search_entry.pack(pady=5, padx=5, fill=tk.X)
        
        listbox_frame = tk.Frame(left_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        question_listbox = tk.Listbox(listbox_frame, font=("Arial", 10), selectmode=tk.SINGLE)
        question_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=question_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        question_listbox.config(yscrollcommand=scrollbar.set)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        tk.Label(right_frame, text="Puni odgovor/objašnjenje:", font=("Arial", 12, "bold")).pack(pady=(0, 5))
        
        self.db_answer_title = tk.Label(right_frame, text="Izaberite pitanje s lijeve strane.", font=("Arial", 14, "italic"), wraplength=400, justify=tk.LEFT)
        self.db_answer_title.pack(pady=10)
        
        self.db_answer_text = scrolledtext.ScrolledText(right_frame, width=40, height=15, font=("Arial", 12), wrap=tk.WORD, state=tk.DISABLED)
        self.db_answer_text.pack(fill="both", expand=True)

        self.question_map = {card['naslov']: card['puni_odgovor'] for card in cards}

        def update_list(search_term=""):
            """Filtrira listu pitanja na osnovu pojma za pretragu."""
            question_listbox.delete(0, tk.END)
            search_term = search_term.lower()
            
            for title in self.question_map.keys():
                if search_term in title.lower():
                    question_listbox.insert(tk.END, title)

        def show_answer(event):
            """Prikazuje odgovor kada se klikne na pitanje u listi."""
            selected_indices = question_listbox.curselection()
            if selected_indices:
                selected_title = question_listbox.get(selected_indices[0])
                answer = self.question_map.get(selected_title, "Odgovor nije pronađen.")
                
                self.db_answer_title.config(text=selected_title)
                
                self.db_answer_text.config(state=tk.NORMAL)
                self.db_answer_text.delete("1.0", tk.END)
                self.db_answer_text.insert(tk.END, answer)
                self.db_answer_text.config(state=tk.DISABLED)

        search_var.trace_add("write", lambda name, index, mode: update_list(search_var.get()))
        question_listbox.bind("<<ListboxSelect>>", show_answer)
        update_list()

    # --- DODAVANJE NOVE KARTICE ---

    def show_add_card_window(self):
        """Kreira prozor za dodavanje novih kartica."""
        add_window = tk.Toplevel(self)
        add_window.title(f"Dodaj Karticu - {self.flashcards.get_subject_name()}")
        add_window.geometry("500x350")

        tk.Label(add_window, text="1. NASLOV KONCEPTA (Pitanje):", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        title_entry = tk.Entry(add_window, width=50, font=("Arial", 12))
        title_entry.pack(pady=5)
        
        tk.Label(add_window, text="2. PUNO OBJAŠNJENJE (Odgovor):", font=("Arial", 12, "bold")).pack(pady=(15, 5))
        answer_text = tk.Text(add_window, width=50, height=5, font=("Arial", 12))
        answer_text.pack(pady=5)
        
        save_btn = tk.Button(add_window, 
                             text="Sačuvaj Novu Karticu", 
                             command=lambda: self.save_new_card(title_entry.get(), answer_text.get("1.0", tk.END), add_window), 
                             bg="green", fg="white", height=2, width=30)
        save_btn.pack(pady=20)
        
    def save_new_card(self, title, answer, window):
        """Logika za spašavanje nove kartice u JSON fajl."""
        title = title.strip()
        answer = answer.strip()
        
        if not title or not answer:
            messagebox.showerror("Greška", "Oba polja moraju biti popunjena!")
            return

        new_card = { "naslov": title, "puni_odgovor": answer }
        
        try:
            with open(self.flashcards.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        data.append(new_card)
        
        try:
            with open(self.flashcards.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Uspjeh", "Kartica je uspješno dodana i spašena!")
            self.flashcards._load_cards()
            window.destroy()
            
        except Exception as e:
            messagebox.showerror("Greška", f"Dogodila se greška prilikom spašavanja: {e}")

    # --- DODAVANJE NOVOG PREDMETA ---

    def add_new_subject(self):
        """Funkcija za kreiranje novog JSON fajla za novi predmet."""
        new_subject = simpledialog.askstring("Novi Predmet", "Unesite naziv novog predmeta (npr. 'historija'):")
        
        if new_subject:
            filename = new_subject.lower().replace(' ', '_') + '.json'
            filepath = os.path.join('data', filename)
            
            if os.path.exists(filepath):
                 messagebox.showerror("Greška", f"Predmet '{new_subject.capitalize()}' već postoji!")
                 return

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=4, ensure_ascii=False)
                
                messagebox.showinfo("Uspjeh", f"Predmet '{new_subject.capitalize()}' je kreiran! Dodajte kartice.")
                self.show_subject_selection_menu()
            except Exception as e:
                messagebox.showerror("Greška", f"Nije moguće kreirati fajl: {e}")

    # --- KVIZ LOGIKA I GUI (AI) ---

    def show_quiz_setup_window(self):
        """Kreira prozor za unos raspona stranica i broja pitanja."""
        
        if not AI_ENABLED:
            messagebox.showerror("Greška", "Gemini AI biblioteka nije instalirana. Pokrenite: pip install google-genai")
            return

        setup_window = tk.Toplevel(self)
        setup_window.title(f"Postavke kviza - {self.flashcards.get_subject_name()}")
        setup_window.geometry("500x350")
        
        tk.Label(setup_window, text="Dokument za učenje:", font=("Arial", 12)).pack(pady=(10, 5))
        
        self.doc_path_var = tk.StringVar(value="Nije odabran PDF fajl")
        tk.Label(setup_window, textvariable=self.doc_path_var, wraplength=450, fg="darkblue").pack()
        
        tk.Button(setup_window, text="Odaberi PDF dokument", command=lambda: self.select_pdf(setup_window)).pack(pady=5)

        frame_pages = tk.Frame(setup_window)
        frame_pages.pack(pady=10)
        
        tk.Label(frame_pages, text="Pitaj me od stranice:").pack(side=tk.LEFT)
        self.start_page_entry = tk.Entry(frame_pages, width=5)
        self.start_page_entry.insert(0, "1")
        self.start_page_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_pages, text="do stranice:").pack(side=tk.LEFT)
        self.end_page_entry = tk.Entry(frame_pages, width=5)
        self.end_page_entry.insert(0, "10")
        self.end_page_entry.pack(side=tk.LEFT, padx=5)

        frame_questions = tk.Frame(setup_window)
        frame_questions.pack(pady=10)
        
        tk.Label(frame_questions, text="Broj pitanja za generiranje:").pack(side=tk.LEFT)
        self.num_questions_entry = tk.Entry(frame_questions, width=5)
        self.num_questions_entry.insert(0, "10")
        self.num_questions_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(setup_window, text="Generiraj i Pokreni Kviz", 
                  command=lambda: self.run_quiz(setup_window), 
                  bg="purple", fg="white", height=2, width=30).pack(pady=20)

    
    def select_pdf(self, window):
        """Otvara dijalog za odabir PDF fajla i čuva putanju."""
        filepath = filedialog.askopenfilename(
            parent=window,
            title="Odaberite dokument",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if filepath:
            self.doc_path_var.set(filepath)


    def run_quiz(self, setup_window):
        """Glavna logika kviza: čita tekst, šalje AI-u i prikazuje pitanja."""
        
        doc_path = self.doc_path_var.get()
        
        if not os.path.exists(doc_path) or doc_path == "Nije odabran PDF fajl":
            messagebox.showerror("Greška", "Molimo odaberite validan PDF dokument.")
            return

        try:
            start_page = int(self.start_page_entry.get())
            end_page = int(self.end_page_entry.get())
            num_questions = int(self.num_questions_entry.get())
            
            if start_page < 1 or end_page < start_page or num_questions < 1:
                raise ValueError("Neispravan unos brojeva stranica ili pitanja.")
        except ValueError as e:
            messagebox.showerror("Greška u unosu", f"Provjerite unos: {e}")
            return
            
        if not os.getenv("GEMINI_API_KEY"):
            messagebox.showerror("Greška", "GEMINI_API_KEY varijabla okruženja nije postavljena.")
            return

        setup_window.destroy()
        
        try:
            full_text = self.extract_text_from_pdf(doc_path, start_page, end_page)
        except Exception as e:
            messagebox.showerror("Greška", f"Ekstrakcija teksta nije uspjela: {e}")
            return

        if not full_text.strip():
            messagebox.showerror("Greška", "Nije moguće izvući tekst iz navedenog raspona stranica.")
            return

        try:
            questions = self.generate_questions_with_ai(full_text, num_questions)
        except APIError as e:
            messagebox.showerror("AI Greška", f"Gemini API nije uspio generirati pitanja. Provjerite ključ ili kvote. Greška: {e}")
            return
        except Exception as e:
            messagebox.showerror("Greška", f"Generiranje pitanja nije uspjelo: {e}")
            return

        if not questions:
            messagebox.showinfo("Kviz", "AI nije uspio generirati pitanja iz teksta.")
            return

        self.show_generated_quiz(questions)


    def extract_text_from_pdf(self, doc_path, start_page, end_page):
        """Ekstrahira tekst iz PDF-a u zadanom rasponu stranica."""
        
        text = ""
        try:
            reader = PdfReader(doc_path)
            for i in range(start_page - 1, end_page):
                if i < len(reader.pages):
                    page = reader.pages[i]
                    text += page.extract_text()
        except Exception as e:
            raise Exception(f"Problem sa čitanjem PDF-a ili rasponom stranica. Provjerite PDF. ({e})")
            
        return text


    def generate_questions_with_ai(self, text, num_questions):
        """Šalje tekst AI-u i traži pitanja i odgovore."""
        
        client = genai.Client()
        
        prompt = f"""
        Ti si stručni asistent za učenje. Tvoja je zadaća generirati visokokvalitetna pitanja i odgovore na osnovu priloženog teksta.

        1. **Broj Pitanja:** Generiraj tačno {num_questions} pitanja.
        2. **Fokus:** Pitanja moraju biti fokusirana na **najvažnije koncepte, datume, formule, definicije ili ključne činjenice** iz teksta. Izbjegavaj irelevantne detalje.
        3. **Odgovor:** Svaki odgovor mora biti **precizan, kratak i direktan**, a ne prepisani dio teksta.
        4. **Format izlaza:** Obavezno vrati izlaz isključivo kao strogi JSON niz (lista objekata). Ne smiješ dodavati nikakav drugi tekst, objašnjenja ili markdown kod (poput ```json) prije ili poslije JSON-a.

        Primjer željenog JSON formata:
        [
            {{
                "pitanje": "Koja je primarna svrha Mitohondrija?",
                "odgovor": "Proizvodnja energije (ATP) staničnim disanjem."
            }},
            {{
                "pitanje": "Navedi datum potpisivanja Dejtonskog sporazuma.",
                "odgovor": "14. decembar 1995. godine."
            }}
        ]

        TEKST ZA ANALIZU:
        ---
        {text}
        ---
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        try:
            json_text = response.text.strip().replace('```json', '').replace('```', '')
            
            if not json_text.startswith('[') and not json_text.endswith(']'):
                raise ValueError("AI izlaz nije u očekivanom JSON formatu (nema zagrada).")
                
            return json.loads(json_text)
        
        except Exception as e:
            print(f"AI izlaz nije validan JSON: {response.text[:200]}...")
            raise Exception(f"AI nije uspio vratiti validan JSON uprkos uputama. ({e})")


    def show_generated_quiz(self, questions):
        """Prikazuje pitanja i odgovore generirane od AI-a u interaktivnom prozoru."""
        
        quiz_window = tk.Toplevel(self)
        quiz_window.title(f"Kviz - {self.flashcards.get_subject_name()} ({len(questions)} pitanja)")
        quiz_window.geometry("750x550")
        
        self.current_quiz_index = -1
        self.quiz_questions = questions
        
        self.quiz_progress_label = tk.Label(quiz_window, text="", font=("Arial", 14, "italic"), fg="grey")
        self.quiz_progress_label.pack(anchor="ne", padx=10, pady=10)
        
        tk.Label(quiz_window, text="Pitanje:", font=("Arial", 10, "italic")).pack(pady=(10, 0))
        self.quiz_question_label = tk.Label(quiz_window, text="Pitanje ide ovdje...", font=("Arial", 18, "bold"), wraplength=700)
        self.quiz_question_label.pack(pady=5)
        
        tk.Label(quiz_window, text="Vaš odgovor:", font=("Arial", 10, "italic")).pack(pady=(10, 0))
        self.quiz_user_answer = scrolledtext.ScrolledText(quiz_window, width=70, height=5, font=("Arial", 12), wrap=tk.WORD)
        self.quiz_user_answer.pack(pady=5)
        
        self.quiz_show_answer_btn = tk.Button(quiz_window, text="Otkrij Tačan Odgovor", command=self.reveal_quiz_answer, width=30, height=2, bg="lightcoral")
        self.quiz_show_answer_btn.pack(pady=10)
        
        self.quiz_ai_answer_label = tk.Label(quiz_window, text="", font=("Arial", 12), fg="blue", wraplength=700, justify=tk.LEFT, bd=2, relief="groove")
        self.quiz_ai_answer_label.pack(pady=10, padx=10, fill=tk.X)
        
        self.quiz_next_btn = tk.Button(quiz_window, text="Sljedeće Pitanje >>", command=self.next_quiz_question, width=30, height=2, bg="lightgreen", state=tk.DISABLED)
        self.quiz_next_btn.pack(pady=20)

        self.next_quiz_question()

    def reveal_quiz_answer(self):
        """Prikazuje točan odgovor generiran od AI-a."""
        if 0 <= self.current_quiz_index < len(self.quiz_questions):
            answer = self.quiz_questions[self.current_quiz_index].get('odgovor', 'Nema odgovora')
            self.quiz_ai_answer_label.config(text=f"Točan odgovor AI-a:\n{answer}")
            self.quiz_show_answer_btn.config(state=tk.DISABLED)
            self.quiz_next_btn.config(state=tk.NORMAL)

    def next_quiz_question(self):
        """Prelazi na sljedeće pitanje u kvizu."""
        self.current_quiz_index += 1
        
        if self.current_quiz_index < len(self.quiz_questions):
            q_data = self.quiz_questions[self.current_quiz_index]
            
            self.quiz_progress_label.config(text=f"Pitanje: {self.current_quiz_index + 1} / {len(self.quiz_questions)}")
            self.quiz_question_label.config(text=q_data.get('pitanje', 'Nema pitanja.'))
            self.quiz_ai_answer_label.config(text="")
            self.quiz_user_answer.delete("1.0", tk.END)
            self.quiz_show_answer_btn.config(state=tk.NORMAL)
            self.quiz_next_btn.config(state=tk.DISABLED)
            
        else:
            messagebox.showinfo("Kviz Završen", "Kviz je uspješno završen!")
            self.quiz_next_btn.master.destroy()


if __name__ == "__main__":
    app = StudijskiProgram()
    app.mainloop()