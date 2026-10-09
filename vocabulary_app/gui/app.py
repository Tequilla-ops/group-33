import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from vocabulary_app.services.dictionary_client import DictionaryClient
from vocabulary_app.services.ai_helper import AIHelper
from vocabulary_app.services.quiz_generator import QuizGenerator
from vocabulary_app.services.spaced_repetition import SpacedRepetitionManager
from vocabulary_app.storage.json_storage import JSONStorage


class VocabularyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vocabulary Learning Application")
        self.root.geometry("900x650")
        self.root.minsize(750, 550)

        # Existing application services
        self.storage = JSONStorage()
        self.dict_client = DictionaryClient(self.storage)
        self.ai_helper = AIHelper()
        self.quiz_gen = QuizGenerator(self.storage)
        self.sr_manager = SpacedRepetitionManager(self.storage)

        # Existing JSON files
        self.words_file = "data/words.json"
        self.flashcards_file = "data/flashcards.json"

        # Application state
        self.current_word = None

        self.quiz_words = []
        self.quiz_index = 0
        self.quiz_score = 0
        self.current_question_data = None

        self.setup_ui()

    def run_app(self):
        self.root.mainloop()

    # =========================================================
    # UI SETUP
    # =========================================================

    def setup_ui(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        self.create_search_tab()
        self.create_saved_words_tab()
        self.create_flashcards_tab()
        self.create_quiz_tab()

    # =========================================================
    # SEARCH
    # =========================================================

    def create_search_tab(self):
        self.search_frame = ttk.Frame(
            self.notebook,
            padding=15
        )

        self.notebook.add(
            self.search_frame,
            text="Search Word"
        )

        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.rowconfigure(2, weight=1)

        ttk.Label(
            self.search_frame,
            text="Enter a word to search:",
            font=("Arial", 11, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 5)
        )

        input_frame = ttk.Frame(self.search_frame)
        input_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 10)
        )

        input_frame.columnconfigure(0, weight=1)

        self.search_entry = ttk.Entry(
            input_frame,
            width=35
        )

        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_word()
        )

        ttk.Button(
            input_frame,
            text="Search",
            command=self.search_word
        ).grid(
            row=0,
            column=1,
            padx=(10, 0)
        )

        self.result_text = tk.Text(
            self.search_frame,
            height=18,
            wrap=tk.WORD
        )

        self.result_text.grid(
            row=2,
            column=0,
            sticky="nsew",
            pady=(0, 10)
        )

        button_frame = ttk.Frame(self.search_frame)
        button_frame.grid(
            row=3,
            column=0,
            sticky="w"
        )

        self.save_word_btn = ttk.Button(
            button_frame,
            text="Save Word",
            command=self.save_word,
            state=tk.DISABLED
        )

        self.save_word_btn.pack(
            side="left",
            padx=(0, 5)
        )

        self.create_flashcard_btn = ttk.Button(
            button_frame,
            text="Create Flashcard",
            command=self.create_flashcard,
            state=tk.DISABLED
        )

        self.create_flashcard_btn.pack(
            side="left"
        )

    def search_word(self):
        term = self.search_entry.get().strip()

        if not term:
            messagebox.showwarning(
                "Missing Word",
                "Please enter a word to search."
            )
            return

        self.result_text.delete("1.0", tk.END)

        self.result_text.insert(
            tk.END,
            f"Searching for '{term}'...\n"
        )

        self.root.update_idletasks()

        try:
            # This is the actual API in DictionaryClient.
            word = self.dict_client.get_word(term)

            if word is None:
                self.current_word = None

                self.save_word_btn.config(
                    state=tk.DISABLED
                )

                self.create_flashcard_btn.config(
                    state=tk.DISABLED
                )

                self.result_text.delete(
                    "1.0",
                    tk.END
                )

                self.result_text.insert(
                    tk.END,
                    f"Word '{term}' was not found.\n\n"
                    "Check the spelling and make sure "
                    "you have an internet connection."
                )

                return

            self.current_word = word

            self.display_word(word)

            self.save_word_btn.config(
                state=tk.NORMAL
            )

            self.create_flashcard_btn.config(
                state=tk.NORMAL
            )

        except ValueError as exc:
            self.current_word = None

            self.save_word_btn.config(
                state=tk.DISABLED
            )

            self.create_flashcard_btn.config(
                state=tk.DISABLED
            )

            self.result_text.delete(
                "1.0",
                tk.END
            )

            self.result_text.insert(
                tk.END,
                str(exc)
            )

        except Exception as exc:
            self.current_word = None

            self.save_word_btn.config(
                state=tk.DISABLED
            )

            self.create_flashcard_btn.config(
                state=tk.DISABLED
            )

            self.result_text.delete(
                "1.0",
                tk.END
            )

            self.result_text.insert(
                tk.END,
                f"Could not search for '{term}'.\n\n"
                f"Error: {exc}"
            )

            messagebox.showerror(
                "Search Error",
                f"Could not search for '{term}'.\n\n{exc}"
            )

    def display_word(self, word):
        self.result_text.delete(
            "1.0",
            tk.END
        )

        term = getattr(word, "term", "")
        pronunciation = getattr(
            word,
            "pronunciation",
            None
        )

        definition = getattr(
            word,
            "definition",
            None
        )

        synonyms = getattr(
            word,
            "synonyms",
            []
        )

        antonyms = getattr(
            word,
            "antonyms",
            []
        )

        ai_explanation = getattr(
            word,
            "ai_explanation",
            None
        )

        memory_trick = getattr(
            word,
            "memory_trick",
            None
        )

        self.result_text.insert(
            tk.END,
            f"WORD: {term.upper()}\n"
        )

        self.result_text.insert(
            tk.END,
            "=" * 50 + "\n\n"
        )

        self.result_text.insert(
            tk.END,
            "Pronunciation:\n"
            f"{pronunciation or 'N/A'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "Definition:\n"
            f"{definition or 'N/A'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "Synonyms:\n"
            f"{', '.join(synonyms) if synonyms else 'None'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "Antonyms:\n"
            f"{', '.join(antonyms) if antonyms else 'None'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "AI Explanation:\n"
            f"{ai_explanation or 'N/A'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "Memory Trick:\n"
            f"{memory_trick or 'N/A'}\n\n"
        )

        self.result_text.insert(
            tk.END,
            "=" * 50
        )

    # =========================================================
    # SAVED WORDS
    # =========================================================

    def save_word(self):
        if not self.current_word:
            messagebox.showwarning(
                "No Word",
                "Search for a word first."
            )
            return

        try:
            words = self.storage.load(
                self.words_file
            )

            term = self.current_word.term

            words[term] = {
                "term": term,
                "pronunciation": self.current_word.pronunciation,
                "definition": self.current_word.definition,
                "synonyms": self.current_word.synonyms,
                "antonyms": self.current_word.antonyms,
                "ai_explanation": self.current_word.ai_explanation,
                "memory_trick": self.current_word.memory_trick,
            }

            success = self.storage.save(
                self.words_file,
                words
            )

            if success:
                self.refresh_saved_words()

                messagebox.showinfo(
                    "Success",
                    f"'{term}' saved successfully!"
                )

            else:
                messagebox.showerror(
                    "Error",
                    "Failed to save word."
                )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not save word.\n\n{exc}"
            )

    def create_saved_words_tab(self):
        self.saved_words_frame = ttk.Frame(
            self.notebook,
            padding=15
        )

        self.notebook.add(
            self.saved_words_frame,
            text="Saved Words"
        )

        self.saved_words_frame.columnconfigure(
            0,
            weight=1
        )

        self.saved_words_frame.rowconfigure(
            1,
            weight=1
        )

        ttk.Label(
            self.saved_words_frame,
            text="Saved Words",
            font=("Arial", 12, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        list_frame = ttk.Frame(
            self.saved_words_frame
        )

        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        list_frame.columnconfigure(
            0,
            weight=1
        )

        list_frame.rowconfigure(
            0,
            weight=1
        )

        self.saved_words_listbox = tk.Listbox(
            list_frame,
            height=18
        )

        self.saved_words_listbox.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.saved_words_listbox.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.saved_words_listbox.config(
            yscrollcommand=scrollbar.set
        )

        self.saved_words_listbox.bind(
            "<<ListboxSelect>>",
            self.select_saved_word
        )

        ttk.Button(
            self.saved_words_frame,
            text="Refresh",
            command=self.refresh_saved_words
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=(10, 0)
        )

        self.refresh_saved_words()

    def refresh_saved_words(self):
        self.saved_words_listbox.delete(
            0,
            tk.END
        )

        try:
            words = self.storage.load(
                self.words_file
            )

            if not words:
                self.saved_words_listbox.insert(
                    tk.END,
                    "No saved words yet."
                )
                return

            for term in sorted(words.keys()):
                self.saved_words_listbox.insert(
                    tk.END,
                    term
                )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not load saved words.\n\n{exc}"
            )

    def select_saved_word(self, event=None):
        selection = self.saved_words_listbox.curselection()

        if not selection:
            return

        selected = self.saved_words_listbox.get(
            selection[0]
        )

        if selected == "No saved words yet.":
            return

        try:
            words = self.storage.load(
                self.words_file
            )

            word_data = None

            for key, data in words.items():
                if key.lower() == selected.lower():
                    word_data = data
                    break

            if not word_data:
                return

            self.result_text.delete(
                "1.0",
                tk.END
            )

            self.result_text.insert(
                tk.END,
                f"WORD: "
                f"{word_data.get('term', selected).upper()}\n"
            )

            self.result_text.insert(
                tk.END,
                "=" * 50 + "\n\n"
            )

            self.result_text.insert(
                tk.END,
                "Pronunciation:\n"
                f"{word_data.get('pronunciation') or 'N/A'}\n\n"
            )

            self.result_text.insert(
                tk.END,
                "Definition:\n"
                f"{word_data.get('definition') or 'N/A'}\n\n"
            )

            synonyms = word_data.get(
                "synonyms",
                []
            )

            antonyms = word_data.get(
                "antonyms",
                []
            )

            self.result_text.insert(
                tk.END,
                "Synonyms:\n"
                f"{', '.join(synonyms) if synonyms else 'None'}\n\n"
            )

            self.result_text.insert(
                tk.END,
                "Antonyms:\n"
                f"{', '.join(antonyms) if antonyms else 'None'}\n\n"
            )

            self.result_text.insert(
                tk.END,
                "AI Explanation:\n"
                f"{word_data.get('ai_explanation') or 'N/A'}\n\n"
            )

            self.result_text.insert(
                tk.END,
                "Memory Trick:\n"
                f"{word_data.get('memory_trick') or 'N/A'}"
            )

            self.notebook.select(
                self.search_frame
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not open saved word.\n\n{exc}"
            )

    # =========================================================
    # FLASHCARDS
    # =========================================================

    def create_flashcards_tab(self):
        self.flashcards_frame = ttk.Frame(
            self.notebook,
            padding=15
        )

        self.notebook.add(
            self.flashcards_frame,
            text="Flashcards"
        )

        self.flashcards_frame.columnconfigure(
            0,
            weight=1
        )

        self.flashcards_frame.rowconfigure(
            1,
            weight=1
        )

        ttk.Label(
            self.flashcards_frame,
            text="Flashcards",
            font=("Arial", 12, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        list_frame = ttk.Frame(
            self.flashcards_frame
        )

        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        list_frame.columnconfigure(
            0,
            weight=1
        )

        list_frame.rowconfigure(
            0,
            weight=1
        )

        self.flashcards_listbox = tk.Listbox(
            list_frame,
            height=18
        )

        self.flashcards_listbox.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.flashcards_listbox.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.flashcards_listbox.config(
            yscrollcommand=scrollbar.set
        )

        button_frame = ttk.Frame(
            self.flashcards_frame
        )

        button_frame.grid(
            row=2,
            column=0,
            sticky="w",
            pady=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Review Selected",
            command=self.review_flashcard
        ).pack(
            side="left",
            padx=(0, 5)
        )

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_flashcards
        ).pack(
            side="left"
        )

        self.refresh_flashcards()

    def refresh_flashcards(self):
        self.flashcards_listbox.delete(
            0,
            tk.END
        )

        try:
            flashcards = self.storage.load(
                self.flashcards_file
            )

            if not flashcards:
                self.flashcards_listbox.insert(
                    tk.END,
                    "No flashcards yet."
                )
                return

            sorted_cards = sorted(
                flashcards.items(),
                key=lambda item: item[1].get(
                    "next_review_date",
                    ""
                )
            )

            for term, data in sorted_cards:
                review_date = data.get(
                    "next_review_date",
                    ""
                )

                if review_date:
                    review_date = review_date[:10]
                else:
                    review_date = "N/A"

                self.flashcards_listbox.insert(
                    tk.END,
                    f"{term} "
                    f"(review: {review_date})"
                )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not load flashcards.\n\n{exc}"
            )

    def create_flashcard(self):
        if not self.current_word:
            messagebox.showwarning(
                "No Word",
                "Search for a word first."
            )
            return

        try:
            flashcards = self.storage.load(
                self.flashcards_file
            )

            term = self.current_word.term

            now = datetime.now().isoformat()

            flashcards[term] = {
                "word": {
                    "term": self.current_word.term,
                    "pronunciation": self.current_word.pronunciation,
                    "definition": self.current_word.definition,
                    "synonyms": self.current_word.synonyms,
                    "antonyms": self.current_word.antonyms,
                    "ai_explanation": self.current_word.ai_explanation,
                    "memory_trick": self.current_word.memory_trick,
                },
                "definition": self.current_word.definition,
                "difficulty": 1,
                "review_count": 0,
                "next_review_date": now,
                "last_reviewed": None,
            }

            success = self.storage.save(
                self.flashcards_file,
                flashcards
            )

            if success:
                self.refresh_flashcards()

                messagebox.showinfo(
                    "Success",
                    f"Flashcard for '{term}' "
                    "created successfully!"
                )

            else:
                messagebox.showerror(
                    "Error",
                    "Failed to save flashcard."
                )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not create flashcard.\n\n{exc}"
            )

    def review_flashcard(self):
        selection = self.flashcards_listbox.curselection()

        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select a flashcard."
            )
            return

        try:
            flashcards = self.storage.load(
                self.flashcards_file
            )

            if not flashcards:
                messagebox.showinfo(
                    "No Flashcards",
                    "There are no flashcards to review."
                )
                return

            sorted_cards = sorted(
                flashcards.items(),
                key=lambda item: item[1].get(
                    "next_review_date",
                    ""
                )
            )

            index = selection[0]

            if index >= len(sorted_cards):
                return

            term, data = sorted_cards[index]

            self.show_flashcard_dialog(
                term,
                data
            )

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Could not open flashcard.\n\n{exc}"
            )

    def show_flashcard_dialog(self, term, data):
        dialog = tk.Toplevel(self.root)

        dialog.title(
            f"Flashcard: {term.capitalize()}"
        )

        dialog.geometry(
            "500x400"
        )

        dialog.transient(
            self.root
        )

        dialog.grab_set()

        word_data = data.get(
            "word",
            {}
        )

        ttk.Label(
            dialog,
            text=word_data.get(
                "term",
                term
            ).upper(),
            font=("Arial", 20, "bold")
        ).pack(
            pady=(25, 10)
        )

        pronunciation = word_data.get(
            "pronunciation"
        )

        if pronunciation:
            ttk.Label(
                dialog,
                text=pronunciation,
                font=("Arial", 11)
            ).pack(
                pady=(0, 15)
            )

        definition_frame = ttk.Frame(
            dialog
        )

        definition_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        definition_label = ttk.Label(
            definition_frame,
            text="Click 'Reveal Definition'",
            wraplength=420,
            justify="center"
        )

        definition_label.pack(
            pady=15
        )

        revealed = [False]

        def reveal_definition():
            if not revealed[0]:
                definition_label.config(
                    text=(
                        "Definition:\n\n"
                        + str(
                            data.get(
                                "definition",
                                "N/A"
                            )
                        )
                    )
                )

                reveal_button.config(
                    state=tk.DISABLED
                )

                revealed[0] = True

        reveal_button = ttk.Button(
            dialog,
            text="Reveal Definition",
            command=reveal_definition
        )

        reveal_button.pack(
            pady=10
        )

        ttk.Label(
            dialog,
            text="How difficult was this card?"
        ).pack(
            pady=(15, 10)
        )

        button_frame = ttk.Frame(
            dialog
        )

        button_frame.pack()

        def update_review(result):
            try:
                success = self.sr_manager.review_card(
                    term,
                    result
                )

                if success:
                    dialog.destroy()

                    self.refresh_flashcards()

                    messagebox.showinfo(
                        "Review Saved",
                        f"Review for '{term}' saved."
                    )

                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to save review."
                    )

            except Exception as exc:
                messagebox.showerror(
                    "Error",
                    f"Could not save review.\n\n{exc}"
                )

        ttk.Button(
            button_frame,
            text="Easy",
            command=lambda: update_review("easy")
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Good",
            command=lambda: update_review("good")
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Hard",
            command=lambda: update_review("hard")
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).grid(
            row=0,
            column=3,
            padx=5
        )

    # =========================================================
    # QUIZ
    # =========================================================

    def create_quiz_tab(self):
        self.quiz_frame = ttk.Frame(
            self.notebook,
            padding=20
        )

        self.notebook.add(
            self.quiz_frame,
            text="Quiz"
        )

        self.quiz_frame.columnconfigure(
            0,
            weight=1
        )

        ttk.Label(
            self.quiz_frame,
            text="Vocabulary Quiz",
            font=("Arial", 16, "bold")
        ).grid(
            row=0,
            column=0,
            pady=(0, 20)
        )

        self.question_label = ttk.Label(
            self.quiz_frame,
            text="Click 'Start Quiz' to begin.",
            wraplength=650,
            justify="center"
        )

        self.question_label.grid(
            row=1,
            column=0,
            pady=(0, 20)
        )

        self.option_var = tk.StringVar(
            value=""
        )

        self.option_buttons = []

        for i in range(4):
            button = ttk.Radiobutton(
                self.quiz_frame,
                text="",
                variable=self.option_var,
                value=""
            )

            button.grid(
                row=2 + i,
                column=0,
                sticky="w",
                padx=30,
                pady=5
            )

            self.option_buttons.append(
                button
            )

        button_frame = ttk.Frame(
            self.quiz_frame
        )

        button_frame.grid(
            row=6,
            column=0,
            pady=20
        )

        ttk.Button(
            button_frame,
            text="Start Quiz",
            command=self.start_quiz
        ).pack(
            side="left",
            padx=5
        )

        self.answer_button = ttk.Button(
            button_frame,
            text="Submit Answer",
            command=self.check_answer,
            state=tk.DISABLED
        )

        self.answer_button.pack(
            side="left",
            padx=5
        )

        self.feedback_label = ttk.Label(
            self.quiz_frame,
            text=""
        )

        self.feedback_label.grid(
            row=7,
            column=0,
            pady=10
        )

        self.score_label = ttk.Label(
            self.quiz_frame,
            text="Score: 0/0"
        )

        self.score_label.grid(
            row=8,
            column=0
        )

    def start_quiz(self):
        try:
            words_pool = self.quiz_gen.get_words_for_quiz(
                count=10
            )

            if len(words_pool) < 4:
                messagebox.showinfo(
                    "Not Enough Words",
                    "You need at least 4 saved words "
                    "to start a quiz."
                )
                return

            self.quiz_words = words_pool

            self.quiz_index = 0
            self.quiz_score = 0
            self.current_question_data = None

            self.score_label.config(
                text="Score: 0/0"
            )

            self.answer_button.config(
                state=tk.NORMAL
            )

            self.ask_question()

        except Exception as exc:
            messagebox.showerror(
                "Quiz Error",
                f"Could not start quiz.\n\n{exc}"
            )

    def ask_question(self):
        if self.quiz_index >= len(
            self.quiz_words
        ):
            self.show_quiz_results()
            return

        try:
            word = self.quiz_words[
                self.quiz_index
            ]

            q_data = self.quiz_gen.generate_question(
                word
            )

            self.current_question_data = q_data

            self.question_label.config(
                text=(
                    f"Question "
                    f"{self.quiz_index + 1} "
                    f"of {len(self.quiz_words)}\n\n"
                    f"{q_data['prompt']}"
                )
            )

            self.option_var.set("")

            options = q_data.get(
                "options",
                []
            )

            for i, button in enumerate(
                self.option_buttons
            ):
                if i < len(options):
                    button.config(
                        text=options[i],
                        value=options[i],
                        state=tk.NORMAL
                    )
                else:
                    button.config(
                        text="",
                        value="",
                        state=tk.DISABLED
                    )

            self.feedback_label.config(
                text=""
            )

            self.score_label.config(
                text=(
                    f"Score: "
                    f"{self.quiz_score}/"
                    f"{self.quiz_index}"
                )
            )

        except Exception as exc:
            messagebox.showerror(
                "Quiz Error",
                f"Could not generate question.\n\n{exc}"
            )

    def check_answer(self):
        if not self.current_question_data:
            messagebox.showinfo(
                "Start Quiz",
                "Click 'Start Quiz' first."
            )
            return

        selected = self.option_var.get()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an answer."
            )
            return

        options = self.current_question_data[
            "options"
        ]

        correct_index = self.current_question_data[
            "correct_index"
        ]

        correct_option = options[
            correct_index
        ]

        if selected == correct_option:
            self.quiz_score += 1

            self.feedback_label.config(
                text="Correct!"
            )

        else:
            self.feedback_label.config(
                text=(
                    "Incorrect. Correct answer: "
                    f"{correct_option}"
                )
            )

        self.quiz_index += 1

        self.answer_button.config(
            state=tk.DISABLED
        )

        self.root.after(
            1000,
            self.next_question
        )

    def next_question(self):
        self.answer_button.config(
            state=tk.NORMAL
        )

        self.ask_question()

    def show_quiz_results(self):
        total = len(
            self.quiz_words
        )

        percentage = (
            (self.quiz_score / total) * 100
            if total
            else 0
        )

        score_record = {
            "total": total,
            "correct": self.quiz_score,
            "percentage": percentage,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            saved = self.quiz_gen.record_score(
                score_record
            )
        except Exception as exc:
            saved = False
            print(
                f"Could not save quiz score: {exc}"
            )

        message = (
            f"Quiz finished!\n\n"
            f"Score: {self.quiz_score}/{total}\n"
            f"Percentage: {percentage:.1f}%"
        )

        if saved:
            message += "\n\nScore saved successfully."

        messagebox.showinfo(
            "Quiz Complete",
            message
        )

        self.question_label.config(
            text="Click 'Start Quiz' to begin."
        )

        self.option_var.set("")

        for button in self.option_buttons:
            button.config(
                text="",
                value="",
                state=tk.NORMAL
            )

        self.feedback_label.config(
            text=""
        )

        self.score_label.config(
            text="Score: 0/0"
        )

        self.answer_button.config(
            state=tk.DISABLED
        )

        self.current_question_data = None
        self.quiz_words = []
        self.quiz_index = 0
        self.quiz_score = 0


if __name__ == "__main__":
    app = VocabularyGUI()
    app.run_app()