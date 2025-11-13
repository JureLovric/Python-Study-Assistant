# 📚 Asistent za učenje (Python GUI Aplikacija)

## Opis Projekta
**Asistent za učenje** je samostalna desktop aplikacija (GUI) razvijena u Pythonu, koristeći `Tkinter` za funkcionalan izgled i **Gemini API** za automatizirano generiranje kvizova.

Glavna svrha je poboljšanje aktivnog učenja putem Flashcard sistema i AI-generiranih testova iz bilo kojeg PDF dokumenta.

## Ključne Funkcionalnosti
* **Flashcards sesije:** Praćenje znanja i ponavljanje kartica koje korisnik označi kao "Nisam znao".
* **Generisanje Kvizova putem AI:** Korištenje Gemini 2.5 Flasha za ekstrakciju teksta iz PDF-a i generiranje visokokvalitetnih, raznolikih pitanja.
* **Lokalna Baza Podataka:** Bilješke i kartice se spašavaju lokalno u JSON formatu.

## Korištene Tehnologije
* Python
* Tkinter (GUI)
* Gemini API (za AI generisanje kvizova)
* PyPDF2 (za ekstrakciju teksta iz PDF-a)

## Pokretanje Projekta
1.  **Kloniranje repozitorija:** `git clone https://www.facebook.com/repoatz/`
2.  **Instalacija dependencies:** `pip install customtkinter pypdf2 google-genai python-dotenv`
3.  **Postavljanje API ključa:** Kreirajte `.env` fajl u korijenskoj mapi i dodajte svoj ključ:
    ```
    GEMINI_API_KEY="VAŠ_KLJUČ_OVJDE"
    ```
4.  **Pokretanje:** `python main.py`