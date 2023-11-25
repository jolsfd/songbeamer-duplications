import tkinter as tk
import similar
import os
import platform
import argparse
import tkinter.filedialog as filedialog
import find
import time

ROW_START = 3
MAX_ITEMS_IN_ROW = 3

EDITOR_LINUX = "gnome-text-editor"
EDITOR_WINDOWS = "notepad.exe"
EDITOR = ""

BACKUP_DIR = os.path.join(os.getcwd(), "backup")

# ensure the backup folder exists
if not os.path.isdir(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)


class Song:
    def __init__(self, duplicates, i: int, j: int) -> None:
        self.i = i
        self.j = j
        self.duplicates = duplicates
        self.path = duplicates[i][j]
        self.btn_open = tk.Button(
            text=os.path.basename(self.path), command=lambda: self.open_editor()
        )
        self.btn_delete = tk.Button(text="Löschen", command=lambda: self.delete_song())

    def open_editor(self):
        os.popen(f'{EDITOR} "{self.path}"')
        return

    def delete_song(self):
        counter = 0
        basename = os.path.basename(self.path)
        new_path = os.path.join(BACKUP_DIR, basename)

        while True:
            if os.path.exists(new_path):
                counter += 1
                new_path = os.path.join(
                    BACKUP_DIR,
                    os.path.splitext(basename)[0]
                    + str(counter)
                    + os.path.splitext(basename)[1],
                )
                continue

            break

        try:
            os.rename(self.path, new_path)

        except:
            print(f"an error occured while moving {self.path}")
            return

        # self.duplicates[self.i].remove(self.path)
        self.remove_from_duplicates()
        self.forget_btns()

        return

    def forget_btns(self):
        self.btn_open.grid_forget()
        self.btn_delete.grid_forget()

    def build_btns(self):
        row_i = 2 * (self.j // MAX_ITEMS_IN_ROW) + ROW_START
        column_i = self.j % MAX_ITEMS_IN_ROW

        #self.btn_open.grid(row=3, column=self.j)
        #self.btn_delete.grid(row=4, column=self.j)
        self.btn_open.grid(row=row_i, column=column_i)
        self.btn_delete.grid(row=row_i+1, column=column_i)

    def remove_from_duplicates(self):
        self.duplicates[self.i].remove(self.path)


class FindSongs:
    def __init__(self, parent) -> None:
        self.root_tk = tk.Tk()
        self.parent = parent

        self.setup_ui()

    def set_entry(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)

    def select_dir(self, entry):
        dir = filedialog.askdirectory()
        self.set_entry(entry, dir)

    def select_file(self, entry):
        file = filedialog.askopenfilename()
        self.set_entry(entry, file)

    def start(self):
        print("neuer Suchlauf gestartet...")

        self.label_progress["text"] = "Suchen..."
        self.parent.destroy()

        # delay for ui changes
        time.sleep(1)

        find.find(self.entry_file.get(), self.entry_dir.get(), self.parent.data_file)

        self.root_tk.destroy()
        self.parent.setup()

        return

    def setup_ui(self):
        self.root_tk.title("Neuer Suchlauf")

        # Ordner auswählen
        self.label_dir = tk.Label(self.root_tk, text="Ordner:")
        self.entry_dir = tk.Entry(self.root_tk)
        self.button_dir = tk.Button(
            self.root_tk,
            text="Auswählen",
            command=lambda: self.select_dir(self.entry_dir),
        )

        # Ordner auswählen
        self.label_erweitert = tk.Label(self.root_tk, text="Erweitert")

        # Datei auswählen
        self.label_file = tk.Label(self.root_tk, text="Datei:")
        self.entry_file = tk.Entry(self.root_tk)
        self.button_file = tk.Button(
            self.root_tk,
            text="Auswählen",
            command=lambda: self.select_file(self.entry_file),
        )

        # Nummer auswählen
        self.label_similar = tk.Label(self.root_tk, text="Ähnlichkeit:")
        self.scale = tk.Scale(self.root_tk, from_=0, to=100, orient=tk.HORIZONTAL)
        self.scale.set(95)

        self.label_unit = tk.Label(self.root_tk, text="Prozent")

        # Suchlauf
        self.btn_start = tk.Button(
            self.root_tk, text="Starten", command=lambda: self.start()
        )
        self.label_progress = tk.Label(self.root_tk, text="")

        # Widgets anordnen
        self.label_dir.grid(row=0, column=0)
        self.entry_dir.grid(row=0, column=1)
        self.button_dir.grid(row=0, column=2)

        self.label_erweitert.grid(row=1, column=0, columnspan=2)

        self.label_file.grid(row=2, column=0)
        self.entry_file.grid(row=2, column=1)
        self.button_file.grid(row=2, column=2)

        self.label_similar.grid(row=4, column=0)
        self.scale.grid(row=4, column=1)
        self.label_unit.grid(row=4, column=2)

        self.btn_start.grid(row=5, column=0)
        self.label_progress.grid(row=5, column=1)


class UI:
    def __init__(self, data_file) -> None:
        self.data_file = data_file
        self.setup()

    def __del__(self):
        self.save_json()

    def setup(self):
        self.duplicates = similar.read_duplicates(self.data_file)
        self.i = -1
        self.songs = []
        self.root_tk = tk.Tk()

        self.setup_ui()
        self.next()

        self.root_tk.mainloop()

    def destroy(self):
        self.root_tk.destroy()

    def save_json(self):
        print("saving edited json...")

        duplications_filtered = filter_duplicates(self.duplicates)
        similar.save_duplicates(self.data_file, duplications_filtered)

    def clear(self):
        for song in self.songs:
            song.forget_btns()

        self.songs = []

    def update(self):
        # delete old widgets
        for song in self.songs:
            song.forget_btns()

        self.songs = []

        # generate new widgets
        for j in range(len(self.duplicates[self.i])):
            song = Song(self.duplicates, self.i, j)

            song.build_btns()

            self.songs.append(song)

        # update progress
        self.progress["text"] = f"{self.i+1} von {len(self.duplicates)}"

    def next(self):
        # check if end is reached
        if self.i == len(self.duplicates) - 1:
            return

        self.i += 1

        self.update()

        return

    def back(self):
        if self.i <= 0:
            return

        self.i -= 1

        self.update()

        return

    def open_all_editor(self):
        for song in self.songs:
            song.open_editor()

        return

    def ignore(self):
        for song in self.songs:
            song.remove_from_duplicates()

        self.next()

        return

    def setup_ui(self):
        self.root_tk.title("Aussortieren")

        self.menu = tk.Menu(self.root_tk)
        self.root_tk.config(menu=self.menu)

        # create menubar
        self.option_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Optionen", menu=self.option_menu)

        self.option_menu.add_command(
            label="Suchlauf", command=lambda: FindSongs(self).root_tk.mainloop()
        )
        # self.option_menu.add_command(
        #     label="Neues Modell trainieren", command=lambda: print("trainieren")
        # ) 
        self.option_menu.add_separator()
        self.option_menu.add_command(label="Beenden", command=self.root_tk.quit)

        # generate widgets
        self.progress = tk.Label(text="")
        self.btn_open_all = tk.Button(
            text="Alle Öffnen", command=lambda: self.open_all_editor()
        )
        self.btn_next = tk.Button(text="Weiter", command=lambda: self.next())
        self.btn_back = tk.Button(text="Zurück", command=lambda: self.back())
        self.btn_ignore = tk.Button(text="Ignorieren", command=lambda: self.ignore())

        # place widgets
        self.progress.grid(row=0, column=0)
        self.btn_open_all.grid(row=0, column=1)
        self.btn_next.grid(row=0, column=3)
        self.btn_back.grid(row=0, column=2)
        self.btn_ignore.grid(row=0, column=4)


def filter_duplicates(duplicates):
    new = []

    for duplicate in duplicates:
        if len(duplicate) <= 1:
            continue

        new.append(duplicate)

    return new


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="GUI for better accessibility", description=""
    )

    parser.add_argument(
        "--data_file",
        type=str,
        default="similar_songs.json",
        help="directory where the trained model lives",
    )

    args = parser.parse_args()

    # set platform editor
    os_name = platform.system()

    if os_name == "Windows":
        EDITOR = EDITOR_WINDOWS

    elif os_name == "Linux":
        EDITOR = EDITOR_LINUX

    UI(args.data_file)
