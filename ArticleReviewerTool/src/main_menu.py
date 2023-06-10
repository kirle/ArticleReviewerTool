import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import pandas as pd
from article_scorer import ArticleScorer

class MainMenu:
    """MainMenu class for creating a GUI using tkinter."""

    def __init__(self, root):
        """Initializes MainMenu instance and UI elements.

        Args:
            root (tk.Tk): The root widget of the tkinter GUI.
        """
        self.root = root
        self.root.configure(background='white')

        self.load_button = self.create_button(text='Load TSV File', command=self.load_file)
        self.article_num_label = self.create_label(text='Enter number of articles to display')
        self.article_num_entry = self.create_spinbox(from_=1, to=10000, default=10)
        self.all_articles_var = tk.IntVar()
        self.all_articles_check = self.create_checkbutton(text='Display all articles', variable=self.all_articles_var, command=self.toggle_articles_selection)
        self.comment_var = tk.IntVar()
        self.comment_check = self.create_checkbutton(text='Allow comments', variable=self.comment_var)
        self.summarize_var = tk.IntVar()
        self.summarize_check = self.create_checkbutton(text='Activate Summarization', variable=self.summarize_var)
        self.output_name_label = self.create_label(text='Enter output file name')
        self.output_name_entry = self.create_entry(default='scores.xlsx')  # Default output file name
        self.start_button = self.create_button(text='Start', command=self.start, state=tk.DISABLED)

        self.articles = None  # Will be set to a list of articles

    def create_button(self, text, command, state=None):
        """Creates and packs a Button widget with the given parameters."""
        button = tk.Button(self.root, text=text, command=command, font=("Helvetica", 16), state=state)
        button.pack(pady=10)
        return button

    def create_label(self, text):
        """Creates and packs a Label widget with the given text."""
        label = tk.Label(self.root, text=text, font=("Helvetica", 16))
        label.pack(pady=10)
        return label

    def create_spinbox(self, from_, to, default):
        """Creates and packs a Spinbox widget with the given parameters."""
        spinbox = tk.Spinbox(self.root, from_=from_, to=to, font=("Helvetica", 16))
        spinbox.pack(pady=10)
        spinbox.delete(0, 'end')
        spinbox.insert(0, default)
        return spinbox

    def create_checkbutton(self, text, variable, command=None):
        """Creates and packs a Checkbutton widget with the given parameters."""
        checkbutton = tk.Checkbutton(self.root, text=text, variable=variable, font=("Helvetica", 16), command=command)
        checkbutton.pack(pady=10)
        return checkbutton

    def create_entry(self, default):
        """Creates and packs an Entry widget with the given default text."""
        entry = tk.Entry(self.root, font=("Helvetica", 16))
        entry.pack(pady=10)
        entry.insert(0, default)
        return entry

    def load_file(self):
        """Opens a File Dialog and loads the selected TSV file into a DataFrame."""
        try:
            filename = filedialog.askopenfilename(initialdir = "/", title = "Select A File", filetypes = (("tsv files","*.tsv"),("all files","*.*")))
            if filename:
                self.articles = pd.read_csv(filename, sep='\t')
                self.start_button['state'] = tk.NORMAL
                num_articles = len(self.articles)  # Number of articles in the loaded file
                self.article_num_entry.config(to=num_articles)
            else:
                messagebox.showerror("Error", "No file selected.")
        except Exception as e_error:
            messagebox.showerror("Error", str(e_error))

    def start(self):
        """Starts the process of scoring and summarizing the articles."""
        try:
            if self.all_articles_var.get() == 1:
                num_articles = len(self.articles)
            else:
                num_articles = int(self.article_num_entry.get())
                if num_articles < 1 or num_articles > len(self.articles):
                     raise ValueError("Please enter a valid number of articles to display.")
            summarization = bool(self.summarize_var.get())
            comment = bool(self.comment_var.get())
            output_filename = self.output_name_entry.get()
            self.root.destroy()
            scorer_root = tk.Tk()
            scorer = ArticleScorer(scorer_root, self.articles, num_articles, summarization, comment, output_filename)
            scorer.start()
            scorer_root.mainloop()
        except ValueError as e_error:
            messagebox.showerror("Error", str(e_error))
        except Exception as e_error:
            messagebox.showerror("Error", str(e_error))

    def toggle_articles_selection(self):
        """Toggles the state of the Spinbox widget based on the Checkbutton's state."""
        if self.all_articles_var.get() == 1:
            self.article_num_entry.config(state='disabled')
        else:
            self.article_num_entry.config(state='normal')
