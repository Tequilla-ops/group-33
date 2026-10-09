import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from vocabulary_app.services.dictionary_client import DictionaryClient
from vocabulary_app.services.ai_helper import AIHelper
from vocabulary_app.services.quiz_generator import QuizGenerator
from vocabulary_app.services.spaced_repetition import SpacedRepetitionManager
from vocabulary_app.storage.json_storage import JSONStorage
from vocabulary_app.models.word import Word
from vocabulary_app.models.flashcard import Flashcard

class VocabularyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vocabulary Learning Application")
        self.storage = JSONStorage()
        self.dict_client = DictionaryClient(self.storage)
        self.ai_helper = AIHelper()
        self.quiz_gen = QuizGenerator(self.storage)
        self.sr_manager = SpacedRepetitionManager(self.storage)
        self.words_file = "data/words.json"
        self.flashcards_file = "data/flashcards.json"
        self.current_word = None
        self.setup_ui()

    def run_app(self):
        self.root.mainloop()

    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Create tabs
        self.search_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.search_frame, text="Search Word")
        self.saved_words_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.saved_words_frame, text="Saved Words")
        self.flashcards_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.flashcards_frame, text="Flashcards")
        self.quiz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.quiz_frame, text="Quiz")
        # Word Search Tab Widgets
        ttk.Label(self.search_frame, text="Enter a word to search:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.search_entry = ttk.Entry(self.search_frame, width=30)
        self.search_entry.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Button(self.search_frame, text="Search", command=self.search_word).grid(row=1, column=1, padx=(5, 0), pady=(0, 10))
        self.result_text = tk.Text(self.search_frame, height=15, width=60, wrap=tk.WORD)
        self.result_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        button_frame = ttk.Frame(self.search_frame)
        button_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        self.save_word_btn = ttk.Button(button_frame, text="Save Word", command=self.save_word, state=tk.DISABLED)
        self.save_word_btn.grid(row=0, column=0, padx=(0, 5))
        self.create_flashcard_btn = ttk.Button(button_frame, text="Create Flashcard", command=self.create_flashcard, state=tk.DISABLED)
        self.create_flashcard_btn.grid(row=0, column=1)
    def display_word(self, word):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"WORD: {word.term.upper()}\\n")
        self.result_text.insert(tk.END, "=" * 40 + "\\n")
        self.result_text.insert(tk.END, f"Pronunciation: {word.pronunciation or 'N/A'}\\n")
        self.result_text.insert(tk.END, f"\\nDefinition:\\n{word.definition or 'N/A'}\\n")
        self.result_text.insert(tk.END, f"\\nSynonyms:\\n{', '.join(word.synonyms) if word.synonyms else 'None'}\\n")
        self.result_text.insert(tk.END, f"\\nAntonyms:\\n{', '.join(word.antonyms) if word.antonyms else 'None'}\\n")
        self.result_text.insert(tk.END, f"\\nAI Explanation:\\n{word.ai_explanation or 'N/A'}\\n")
        self.result_text.insert(tk.END, f"\\nMemory Trick:\\n{word.memory_trick or 'N/A'}\\n")
        self.result_text.insert(tk.END, "=" * 40 + "\\n")
    def save_word(self):
        if self.current_word:
            words = self.storage.load(self.words_file)
            words[self.current_word.term] = {
                \"term\": self.current_word.term,
                \"pronunciation\": self.current_word.pronunciation,
                \"definition\": self.current_word.definition,
                \"synonyms\": self.current_word.synonyms,
                \"antonyms\": self.current_word.antonyms,
                \"ai_explanation\": self.current_word.ai_explanation,
                \"memory_trick\": self.current_word.memory_trick,
            }
            if self.storage.save(self.words_file, words):
                messagebox.showinfo(\"Success\", f\"'{self.current_word.term}' saved successfully!\")
            else:
                messagebox.showerror(\"Error\", \"Failed to save word.\")

    def create_flashcard(self):
        if self.current_word:
            flashcards = self.storage.load(self.flashcards_file)
            flashcards[self.current_word.term] = {
                \"word\": {
                    \"term\": self.current_word.term,
                    \"pronunciation\": self.current_word.pronunciation,
                    \"definition\": self.current_word.definition,
                    \"synonyms\": self.current_word.synonyms,
                    \"antonyms\": self.current_word.antonyms,
                    \"ai_explanation\": self.current_word.ai_explanation,
                    \"memory_trick\": self.current_word.memory_trick,
                },
                \"definition\": self.current_word.definition,
                \"difficulty\": 1,
                \"review_count\": 0,
                \"next_review_date\": datetime.now().isoformat(),
                \"last_reviewed\": datetime.now().isoformat(),
            }
            if self.storage.save(self.flashcards_file, flashcards):
                messagebox.showinfo(\"Success\", f\"Flashcard for '{self.current_word.term}' created successfully!\")
            else:
                messagebox.showerror(\"Error\", \"Failed to create flashcard.\")
        self.saved_words_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.saved_words_frame, text="Saved Words")
        self.flashcards_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.flashcards_frame, text="Flashcards")
        self.quiz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.quiz_frame, text="Quiz")
    # Saved Words Tab Widgets
        ttk.Label(self.saved_words_frame, text=\"Saved Words:\").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.saved_words_listbox = tk.Listbox(self.saved_words_frame, height=15, width=50)
        self.saved_words_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        ttk.Button(self.saved_words_frame, text=\"Refresh\", command=self.refresh_saved_words).grid(row=1, column=1, padx=(5, 0), pady=(0, 10))
        self.refresh_saved_words()
    def refresh_saved_words(self):
        self.saved_words_listbox.delete(0, tk.END)
        words = self.storage.load(self.words_file)
        for term in sorted(words.keys()):
            self.saved_words_listbox.insert(tk.END, term.capitalize())

    # Flashcards Tab Widgets
        ttk.Label(self.flashcards_frame, text=\"Flashcards (review date order):\").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.flashcards_listbox = tk.Listbox(self.flashcards_frame, height=15, width=50)
        self.flashcards_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        ttk.Button(self.flashcards_frame, text=\"Review Selected\", command=self.review_flashcard).grid(row=1, column=1, padx=(5, 0), pady=(0, 10))
        ttk.Button(self.flashcards_frame, text=\"Refresh\", command=self.refresh_flashcards).grid(row=2, column=0, padx=(0, 5), pady=(5, 0))
        self.refresh_flashcards()

    def refresh_flashcards(self):
        self.flashcards_listbox.delete(0, tk.END)
        flashcards = self.storage.load(self.flashcards_file)
        # Sort by next_review_date
        sorted_cards = sorted(flashcards.items(), key=lambda x: x[1].get('next_review_date', ''))
        for term, data in sorted_cards:
            self.flashcards_listbox.insert(tk.END, f\"{term.capitalize()} (review: {data.get('next_review_date', '')[:10]})\")

    def review_flashcard(self):
        selection = self.flashcards_listbox.curselection()
        if not selection:
            messagebox.showwarning(\"No Selection\", \"Please select a flashcard to review.\")
            return
        index = selection[0]
        flashcards = self.storage.load(self.flashcards_file)
        terms = list(flashcards.keys())
        term = terms[index]
        data = flashcards[term]
        
        # Show flashcard dialog
        self.show_flashcard_dialog(term, data)

    def show_flashcard_dialog(self, term, data):
        dialog = tk.Toplevel(self.root)
        dialog.title(f\"Flashcard: {term.capitalize()}\")
        dialog.geometry(\"400x300\")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Word info
        word_data = data.get('word', {})
        ttk.Label(dialog, text=f\"WORD: {word_data.get('term', '').upper()}\", font=(\"Arial\", 14, \"bold\")).pack(pady=10)
        ttk.Label(dialog, text=f\"Definition: {data.get('definition', 'N/A')}\", wraplength=350).pack(pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        def update_review(result):
            if self.sr_manager.review_card(term, result):
                dialog.destroy()
                self.refresh_flashcards()
                messagebox.showinfo(\"Review Saved\", f\"Your review for '{term}' has been recorded.\")
            else:
                messagebox.showerror(\"Error\", \"Failed to save review.\")
        
        ttk.Button(btn_frame, text=\"Easy\", command=lambda: update_review(\"easy\")).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text=\"Good\", command=lambda: update_review(\"good\")).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text=\"Hard\", command=lambda: update_review(\"hard\")).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text=\"Cancel\", command=dialog.destroy).grid(row=0, column=3, padx=5)
    # Quiz Tab Widgets
        ttk.Label(self.quiz_frame, text=\"Vocabulary Quiz\").grid(row=0, column=0, columnspan=2, pady=(0, 20))
        self.question_label = ttk.Label(self.quiz_frame, text=\"Click 'Start Quiz' to begin\", wraplength=400)
        self.question_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        self.option_vars = []
        self.option_buttons = []
        for i in range(4):
            var = tk.StringVar()
            self.option_vars.append(var)
            rb = ttk.Radiobutton(self.quiz_frame, text=\"\", variable=var, value=\"\")
            rb.grid(row=2+i, column=0, columnspan=2, sticky=tk.W, padx=20, pady=5)
            self.option_buttons.append(rb)
        ttk.Button(self.quiz_frame, text=\"Start Quiz\", command=self.start_quiz).grid(row=6, column=0, columnspan=2, pady=20)
        self.feedback_label = ttk.Label(self.quiz_frame, text=\"\", foreground=\"green\")
        self.feedback_label.grid(row=7, column=0, columnspan=2, pady=(0, 10))
        self.score_label = ttk.Label(self.quiz_frame, text=\"Score: 0/0\")
        self.score_label.grid(row=8, column=0, columnspan=2)

    def start_quiz(self):
        words_pool = self.quiz_gen.get_words_for_quiz(count=10)
        if len(words_pool) < 2:
            messagebox.showinfo(\"Not Enough Words\", \"Need at least 2 saved words to start a quiz. Search & save more words first!\")
            return
        self.quiz_words = words_pool
        self.quiz_index = 0
        self.quiz_score = 0
        self.ask_question()

    def ask_question(self):
        if self.quiz_index >= len(self.quiz_words):
            self.show_quiz_results()
            return
        word = self.quiz_words[self.quiz_index]
        q_data = self.quiz_gen.generate_question(word)
        self.current_question_data = q_data
        self.question_label.config(text=q_data['prompt'])
        for i, (var, btn) in enumerate(zip(self.option_vars, self.option_buttons)):
            if i < len(q_data['options']):
                var.set(q_data['options'][i])
                btn.config(text=q_data['options'][i])
            else:
                var.set(\"\")
                btn.config(text=\"\")
        # Clear previous selection
        for var in self.option_vars:
            var.set(\"\")
        self.feedback_label.config(text=\"\")

    def check_answer(self):
        selected = None
        for var in self.option_vars:
            if var.get():
                selected = var.get()
                break
        if not selected:
            messagebox.showwarning(\"No Selection\", \"Please select an answer.\")
            return
        correct_index = self.current_question_data['correct_index']
        correct_option = self.current_question_data['options'][correct_index]
        if selected == correct_option:
            self.quiz_score += 1
            self.feedback_label.config(text=\"Correct!\", foreground=\"green\")
        else:
            self.feedback_label.config(text=f\"Incorrect. Correct answer: {correct_option}\", foreground=\"red\")
        self.quiz_index += 1
        # Disable buttons temporarily to prevent rapid clicking
        for btn in self.option_buttons:
            btn.config(state=\"disabled\")
        self.quiz_frame.after(1000, self.next_question)

    def next_question(self):
        for btn in self.option_buttons:
            btn.config(state=\"normal\")
        self.ask_question()

    def show_quiz_results(self):
        percentage = (self.quiz_score / len(self.quiz_words)) * 100 if self.quiz_words else 0
        messagebox.showinfo(\"Quiz Complete\", f\"Quiz finished! Score: {self.quiz_score}/{len(self.quiz_words)} ({percentage:.1f}%)\")
        # Record score
        score_record = {
            \"total\": len(self.quiz_words),
            \"correct\": self.quiz_score,
            \"percentage\": percentage,
            \"timestamp\": datetime.now().isoformat(),
        }
        self.quiz_gen.record_score(score_record)
        # Reset UI
        self.question_label.config(text=\"Click 'Start Quiz' to begin\")
        for var in self.option_vars:
            var.set(\"\")
        self.feedback_label.config(text=\"\")
        self.score_label.config(text=\"Score: 0/0\")
if __name__ == "__main__":
    app = VocabularyGUI()
    app.run_app()
