import tkinter as tk
import duplications
import os
import platform
import argparse

EDITOR_LINUX = "gnome-text-editor"
EDITOR_WINDOWS = "edit"
EDITOR = ""

BACKUP_DIR = os.path.join(os.getcwd(), "backup")


class Song:
    def __init__(self, duplicates, i: int, j: int) -> None:
        self.i = i
        self.j = j
        self.duplicates = duplicates
        self.path = duplicates[i][j]
        self.btn_open = tk.Button(
            text=os.path.basename(self.path), command=lambda: self.open_editor()
        )
        self.btn_delete = tk.Button(text="Delete", command=lambda: self.delete_song())

    def open_editor(self):
        os.popen(f"{EDITOR} '{self.path}'")
        return

    def delete_song(self):
        new_path = os.path.join(BACKUP_DIR, os.path.basename(self.path))

        try:
            os.rename(self.path, new_path)

        except:
            print(f"an error occured while moving {self.path}")
            return

        self.duplicates[self.i].remove(self.path)
        self.forget_btns()
        return

    def forget_btns(self):
        self.btn_open.grid_forget()
        self.btn_delete.grid_forget()

    def build_btns(self):
        self.btn_open.grid(row=3, column=self.j)
        self.btn_delete.grid(row=4, column=self.j)


class UI:
    def __init__(self) -> None:
        self.duplicates = [[]]
        self.i = -1
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
        raw = ""

        for song in self.songs:
            raw += f"'{song.path}' "

        os.popen(f"{EDITOR} {raw}")
        return

    def setup_ui(self):
        # generate widgets
        self.progress = tk.Label(text="")
        self.btn_open_all = tk.Button(
            text="Open all", command=lambda: self.open_all_editor()
        )
        self.btn_next = tk.Button(text="Next", command=lambda: self.next())
        self.btn_back = tk.Button(text="Back", command=lambda: self.back())

        # place widgets
        self.progress.grid(row=0, column=0)
        self.btn_open_all.grid(row=0, column=1)
        self.btn_next.grid(row=0, column=3)
        self.btn_back.grid(row=0, column=2)


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

    # create window
    window = tk.Tk()
    window.title("Aussortieren")

    # initial object
    ui = UI()

    ui.duplicates = duplications.read_duplicates(args.data_file)
    ui.setup_ui()
    ui.next()

    # mainloop
    window.mainloop()

    # saving data persistent
    print("saving edited json...")

    duplications_filtered = filter_duplicates(ui.duplicates)
    duplications.save_duplicates(args.data_file, duplications_filtered)
