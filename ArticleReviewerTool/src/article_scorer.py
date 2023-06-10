import tkinter as tk
from tkinter import ttk, messagebox
import _tkinter
from transformers import pipeline
import pandas as pd


class ArticleScorer:
    def __init__(self, root, articles, max_articles, summarize, comment, output_filename):
        self.root = root
        self.root.configure(background='white')
        self.articles = articles
        self.max_articles = max_articles
        self.current_article = 0
        self.actual_article = 0  

        self.scores = {}  
        self.comments = []
        self.summarize = summarize
        self.comment = comment
        self.output_filename = output_filename
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Create a canvas with a scrollbar
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame to hold all the content and add it to the canvas
        self.main_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # scorer layout

        self.current_article_label = tk.Label(self.main_frame, text='Article: 0/0', font=("Helvetica", 18, 'bold'), bg='light yellow')
        self.current_article_label.pack(pady=5, expand=True)

        self.title_label = tk.Label(self.main_frame, text='Title:', font=("Helvetica", 18, 'bold'), bg='light yellow')
        self.title_label.pack(pady=5)
        self.title_text = tk.Text(self.main_frame, height=2, width=80, font=("Helvetica", 18), wrap="word", padx=20, pady=20, bg="light yellow", state='disabled')
        self.title_text.pack(padx=10, pady=5)

        self.author_label = tk.Label(self.main_frame, text='Author:', font=("Helvetica", 18, 'bold'), bg='light yellow')
        self.author_label.pack(pady=5)
        self.author_text = tk.Text(self.main_frame, height=2, width=80, font=("Helvetica", 18), wrap="word", padx=20, pady=20, bg="light yellow", state='disabled')
        self.author_text.pack(padx=10, pady=5)

        self.year_label = tk.Label(self.main_frame, text='Year:', font=("Helvetica", 18, 'bold'), bg='light yellow')
        self.year_label.pack(pady=5)
        self.year_text = tk.Text(self.main_frame, height=2, width=80, font=("Helvetica", 18), wrap="word", padx=20, pady=20, bg="light yellow", state='disabled')
        self.year_text.pack(padx=10, pady=5)

        self.abstract_label = tk.Label(self.main_frame, text='Abstract:', font=("Helvetica", 18, 'bold'), bg='light yellow')
        self.abstract_label.pack(pady=5)
        self.abstract_text = tk.Text(self.main_frame, height=10, width=80, font=("Helvetica", 18), wrap="word", padx=20, pady=20, bg="light yellow", state='disabled')
        self.abstract_text.pack(padx=10, pady=5)

        if (self.summarize):
            self.summary_label = tk.Label(self.main_frame, text='Summary:', font=("Helvetica", 18, 'bold'), bg='light yellow')
            self.summary_label.pack(pady=5)
            self.summary_text = tk.Text(self.main_frame, height=10, width=80, font=("Helvetica", 18), wrap="word", padx=20, pady=20, bg="light yellow", state='disabled')
            self.summary_text.pack(padx=10, pady=5)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.score_buttons = []
        for i in range(4):
            button = tk.Button(self.button_frame, text=str(i), command=lambda i=i: self.score_article(i), font=("Helvetica", 16), width=2)
            button.pack(side=tk.LEFT, padx=20)
            self.score_buttons.append(button)

        if comment:
            self.comment_label = tk.Label(self.main_frame, text='Comments', font=("Helvetica", 16))
            self.comment_label.pack(pady=10)

            self.comment_entry = tk.Text(self.main_frame, height=5, width=50, font=("Helvetica", 16))
            self.comment_entry.pack(pady=10)

        self.quit_button = tk.Button(self.main_frame, text='Finish', command=self.export_scores, font=("Helvetica", 16))
        self.quit_button.pack(pady=10)

        self.instruction_label = tk.Label(self.main_frame, text="Press 0, 1, or 2 to score an article, and 'Finish' when done.", font=("Helvetica", 18), bg='white')
        self.instruction_label.pack(pady=10)

        # header menu for changing font
        self.fonts = ["Helvetica", "Arial", "Times New Roman", "Courier", "Verdana"]  # define a list of available fonts
        self.menu_bar = tk.Menu(root)  # create a new menu bar
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Change Font", command=self.create_font_window)

        # header menu to goto
       
        self.file_menu.add_command(label="Go to Article", command=self.create_goto_window)
        self.menu_bar.add_cascade(label="Options", menu=self.file_menu)
        root.config(menu=self.menu_bar)

        # list of all widgets to change font
        self.all_widgets = [self.title_label, self.title_text, self.author_label, self.author_text, self.year_label, self.year_text,
                            self.abstract_label, self.abstract_text, self.button_frame] + self.score_buttons + [self.instruction_label]
        if comment:
            self.all_widgets.extend([self.comment_label, self.comment_entry])
        if self.summarize:
            self.all_widgets.extend([self.summary_label, self.summary_text])
        self.all_widgets.append(self.quit_button)

    def create_goto_window(self):
        self.goto_window = tk.Toplevel(self.root)
        self.goto_window.title("Go to Article")
        self.goto_article_entry_window = tk.Entry(self.goto_window, font=("Helvetica", 16))
        self.goto_article_entry_window.pack(pady=10)
        self.goto_article_button_window = tk.Button(self.goto_window, text='Go', command=self.go_to_article_window, font=("Helvetica", 16))
        self.goto_article_button_window.pack(pady=10)

    def go_to_article_window(self):
        try:
            article_num = int(self.goto_article_entry_window.get()) - 1  
            if article_num >= 0 and article_num < self.max_articles:
                self.current_article = article_num
                self.actual_article = article_num
                self.display_article()
                self.goto_window.destroy()  
            else:
                messagebox.showerror("Error", "Invalid article number.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            

    def create_font_window(self):
        self.font_window = tk.Toplevel(self.root)
        self.font_window.title("Change Font")
        self.selected_font = tk.StringVar(self.font_window)
        self.selected_font.set(self.fonts[0])  # set default value
        self.font_optionmenu = tk.OptionMenu(self.font_window, self.selected_font, *self.fonts)
        self.font_optionmenu.pack()
        self.change_font_button = tk.Button(self.font_window, text="Change Font", command=self.change_font)
        self.change_font_button.pack()

    def change_font(self):
        selected_font = self.selected_font.get()  # get selected font
        for widget in self.all_widgets:
            try:
                widget.config(font=(selected_font, 18))
            except _tkinter.TclError:
                pass
        self.font_window.destroy()  



    def display_article(self):
        if self.actual_article < self.max_articles:  
            article = self.articles.iloc[self.actual_article]  #

            self.current_article_label['text'] = f'Article: {self.current_article+1}/{self.max_articles}'
            
            self.title_text.config(state='normal')
            self.title_text.delete('1.0', 'end')
            self.title_text.insert('1.0', article['Title Primary'])  
            self.title_text.config(state='disabled')

            self.author_text.config(state='normal')
            self.author_text.delete('1.0', 'end')
            self.author_text.insert('1.0', article['Authors, Primary'])  
            self.author_text.config(state='disabled')

            self.year_text.config(state='normal')
            self.year_text.delete('1.0', 'end')
            self.year_text.insert('1.0', str(article['Pub Year']))  
            self.year_text.config(state='disabled')


            self.abstract_text.config(state='normal')
            self.abstract_text.delete('1.0', 'end')
            self.abstract_text.insert('1.0', article['Abstract'])  
            self.abstract_text.config(state='disabled')

            if self.summarize:
                summary = self.summarizer(article['Abstract'], max_length=150, do_sample=False)[0]['summary_text']  
                self.summary_text.config(state='normal')
                self.summary_text.delete('1.0', 'end')
                self.summary_text.insert('1.0', summary)
                self.summary_text.config(state='disabled')
        else:
            messagebox.showinfo("End", "All articles have been reviewed.")
            self.export_scores()


    def score_article(self, score):
            if self.current_article < self.max_articles:  
                try:  
                    self.scores[self.actual_article] = score
                    if self.comment:
                        comment = self.comment_entry.get('1.0', 'end-1c')
                        self.comments.append(comment if comment.strip() != '' else 'No comment')  
                        self.comment_entry.delete('1.0', 'end')
                    self.current_article += 1
                    self.actual_article = self.current_article
                    self.display_article()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                    self.export_scores() 


    def export_scores(self):
        df = pd.DataFrame({
            'Title': self.articles['Title Primary'][:self.max_articles],              
            'Author': self.articles['Authors, Primary'][:self.max_articles],  
            'Year': self.articles['Pub Year'][:self.max_articles],  
            'Score': [self.scores.get(i, None) for i in range(self.max_articles)],  
            'Comments': [self.comments[i] if i < len(self.comments) else 'No comment' for i in range(self.max_articles)]
        })

        with pd.ExcelWriter(self.output_filename) as writer:
            df.to_excel(writer, index=False)
        self.root.destroy()  




    def start(self):
        self.display_article()