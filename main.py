import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "notes.json"

def load_notes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_notes(notes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)

class DailyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ежедневник")
        self.notes = load_notes()

        # Поля ввода с плейсхолдерами
        frame_input = tk.Frame(root)
        frame_input.pack(pady=5, padx=10, fill="x")

        self.entry_date = ttk.Entry(frame_input, width=14)
        self.entry_date.insert(0, "ГГГГ-ММ-ДД")
        self.entry_date.bind("<FocusIn>", lambda e: self._clear_placeholder(self.entry_date, "ГГГГ-ММ-ДД"))
        self.entry_date.bind("<FocusOut>", lambda e: self._add_placeholder(self.entry_date, "ГГГГ-ММ-ДД"))
        self.entry_date.grid(row=0, column=0, padx=5)

        self.entry_text = ttk.Entry(frame_input, width=40)
        self.entry_text.insert(0, "Текст заметки")
        self.entry_text.bind("<FocusIn>", lambda e: self._clear_placeholder(self.entry_text, "Текст заметки"))
        self.entry_text.bind("<FocusOut>", lambda e: self._add_placeholder(self.entry_text, "Текст заметки"))
        self.entry_text.grid(row=0, column=1, padx=5)

        btn_add = tk.Button(frame_input, text="Добавить заметку", command=self.add_note)
        btn_add.grid(row=0, column=2, padx=5)

        # Списки дат и заметок
        frame_lists = tk.Frame(root)
        frame_lists.pack(pady=5, padx=10, fill="both", expand=True)

        self.listbox_dates = tk.Listbox(frame_lists, width=15, height=10)
        self.listbox_dates.grid(row=0, column=0, padx=(0,5))
        self.listbox_dates.bind("<<ListboxSelect>>", self.on_date_select)

        self.listbox_notes = tk.Listbox(frame_lists, width=50, height=10)
        self.listbox_notes.grid(row=0, column=1)

        # Кнопки управления
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=5, padx=10, fill="x")

        tk.Button(frame_buttons, text="Удалить заметку", command=self.delete_selected_note).grid(row=0, column=0, padx=5)
        tk.Button(frame_buttons, text="Очистить дату", command=self.clear_date).grid(row=0, column=1, padx=5)
        tk.Button(frame_buttons, text="Обновить", command=self.refresh_lists).grid(row=0, column=2, padx=5)
        tk.Button(frame_buttons, text="Выход", command=root.destroy).grid(row=0, column=3, padx=5)

        # Поиск
        frame_search = tk.Frame(root)
        frame_search.pack(pady=5, padx=10, fill="x")

        self.entry_search = ttk.Entry(frame_search, width=30)
        self.entry_search.insert(0, "Поиск...")
        self.entry_search.bind("<FocusIn>", lambda e: self._clear_placeholder(self.entry_search, "Поиск..."))
        self.entry_search.bind("<FocusOut>", lambda e: self._add_placeholder(self.entry_search, "Поиск..."))
        self.entry_search.grid(row=0, column=0, padx=5)

        tk.Button(frame_search, text="Искать", command=self.search_notes).grid(row=0, column=1, padx=5)

        self.refresh_lists()

    def _clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground="black")

    def _add_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="gray")

    def refresh_lists(self):
        self.listbox_dates.delete(0, tk.END)
        for date in sorted(self.notes.keys()):
            count = len(self.notes[date])
            self.listbox_dates.insert(tk.END, f"{date} ({count})")
        self.listbox_notes.delete(0, tk.END)

    def on_date_select(self, event):
        selection = self.listbox_dates.curselection()
        if not selection:
            return
        date_str = self.listbox_dates.get(selection[0])
        date = date_str.split(" (")[0]
        self.listbox_notes.delete(0, tk.END)
        if date in self.notes:
            for note in self.notes[date]:
                self.listbox_notes.insert(tk.END, note)

    def add_note(self):
        date = self.entry_date.get().strip()
        text = self.entry_text.get().strip()
        if not date or not text or date == "ГГГГ-ММ-ДД" or text == "Текст заметки":
            messagebox.showwarning("Внимание", "Заполните дату и текст.")
            return
        if date in self.notes:
            self.notes[date].append(text)
        else:
            self.notes[date] = [text]
        save_notes(self.notes)
        self.entry_date.delete(0, tk.END)
        self.entry_text.delete(0, tk.END)
        self._add_placeholder(self.entry_date, "ГГГГ-ММ-ДД")
        self._add_placeholder(self.entry_text, "Текст заметки")
        self.refresh_lists()
        for i in range(self.listbox_dates.size()):
            if self.listbox_dates.get(i).startswith(date):
                self.listbox_dates.selection_set(i)
                self.listbox_dates.event_generate("<<ListboxSelect>>")
                break

    def delete_selected_note(self):
        sel_date = self.listbox_dates.curselection()
        if not sel_date:
            messagebox.showwarning("Внимание", "Сначала выберите дату.")
            return
        date_str = self.listbox_dates.get(sel_date[0])
        date = date_str.split(" (")[0]
        sel_note = self.listbox_notes.curselection()
        if not sel_note:
            messagebox.showwarning("Внимание", "Выделите заметку.")
            return
        note_index = sel_note[0]
        if date not in self.notes or note_index >= len(self.notes[date]):
            messagebox.showerror("Ошибка", "Заметка не найдена.")
            return
        self.notes[date].pop(note_index)
        if not self.notes[date]:
            del self.notes[date]
        save_notes(self.notes)
        self.refresh_lists()
        if date in self.notes:
            for i in range(self.listbox_dates.size()):
                if self.listbox_dates.get(i).startswith(date):
                    self.listbox_dates.selection_set(i)
                    self.listbox_dates.event_generate("<<ListboxSelect>>")
                    break

    def clear_date(self):
        sel_date = self.listbox_dates.curselection()
        if not sel_date:
            messagebox.showwarning("Внимание", "Выберите дату.")
            return
        date_str = self.listbox_dates.get(sel_date[0])
        date = date_str.split(" (")[0]
        if date not in self.notes:
            messagebox.showinfo("Информация", "Нет заметок.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить все заметки за {date}?"):
            del self.notes[date]
            save_notes(self.notes)
            self.refresh_lists()

    def search_notes(self):
        query = self.entry_search.get().strip()
        if not query or query == "Поиск...":
            messagebox.showwarning("Внимание", "Введите текст для поиска.")
            return
        results = []
        query_lower = query.lower()
        for date, note_list in self.notes.items():
            for note in note_list:
                if query_lower in note.lower():
                    results.append((date, note))
        if not results:
            messagebox.showinfo("Результат", "Ничего не найдено.")
            return

        result_win = tk.Toplevel(self.root)
        result_win.title(f"Поиск: '{query}'")
        result_win.geometry("500x300")

        scrollbar = tk.Scrollbar(result_win)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(result_win, yscrollcommand=scrollbar.set, width=70, height=15)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=listbox.yview)

        for date, note in results:
            listbox.insert(tk.END, f"{date} — {note}")

        def on_result_select(event):
            sel = listbox.curselection()
            if not sel:
                return
            text = listbox.get(sel[0])
            date = text.split(" — ")[0]
            for i in range(self.listbox_dates.size()):
                if self.listbox_dates.get(i).startswith(date):
                    self.listbox_dates.selection_clear(0, tk.END)
                    self.listbox_dates.selection_set(i)
                    self.listbox_dates.event_generate("<<ListboxSelect>>")
                    self.root.lift()
                    break

        listbox.bind("<Double-Button-1>", on_result_select)

if __name__ == "__main__":
    root = tk.Tk()
    app = DailyPlannerApp(root)
    root.mainloop()