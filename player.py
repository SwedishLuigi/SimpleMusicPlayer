import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pygame as p
import time as t
import os
from mutagen import File

p.mixer.init()

file_path = None
track_list = None
volume = 0.5
manual_stop = False
auto_switch = False

def raise_Error(error="", window_title="", type=""):
    if type == "warning":
        messagebox.showwarning(window_title, error)
        return

    messagebox.showerror(window_title, error)
    
def play_custom_Track(event):
    global track_list_index

    try:
        selected_track = visual_track_list.selection()
        if selected_track:
            selected_track_index = selected_track[0]
            selected_track_title = visual_track_list.item(selected_track_index, "values")[0]
            
            for index, track in enumerate(track_list):
                if os.path.basename(track) == selected_track_title:
                    track_list_index = index
                    break
    except IndexError:
        raise_Error("Failed to fetch track;", "Error")
        return
    except Exception as e:
        raise_Error(f"An error has occoured;\n{e}", "Error")
        return

    play_Audio(track_list, track_list_index)

def play_Audio(track_list, track_list_index):
    global current_track
    global manual_stop

    try:
        current_track = track_list[track_list_index]
        
        p.mixer.music.load(track_list[track_list_index])
        p.mixer.music.set_volume(volume)
        
        update_play_button("pause_button")
        update_window_title("playing")
        
        p.mixer.music.play()
        manual_stop = False
        initialize_progress_bar(current_track)
    except p.error as e:
        raise_Error(f"Error while loading track.\n{e}", "Error")
        return
    except FileNotFoundError:
        raise_Error(f"No file found in path: {track_list[track_list_index]};", "Error")
        return

    check_for_track_end()

def pause_Audio():
    global manual_stop
    global auto_switch

    try:
        p.mixer.music.pause()
        manual_stop = True
        auto_switch = False
        update_play_button("resume_button")
        update_window_title("stopped")
    except p.error as e:
        raise_Error(f"Error while pausing audio\n{e}", "Error")
        return
    except Exception as e:
        raise_Error(f"An error occoured;\n{e}", "Error")
        return

def unpause_Audio():
    global manual_stop
    global auto_switch

    try:
        p.mixer.music.unpause()
        manual_stop = False
        auto_switch = True
        update_progress_bar()
        update_play_button("pause_button")
        update_window_title("playing")
    except p.error as e:
        raise_Error(f"Error while unpausing audio\n{e}", "Error")
        return
    except Exception as e:
        raise_Error(f"An error occoured;{e}\n", "Error")
        return

def next_Track(track_list):
    global track_list_index
    global auto_switch

    try:
        track_list_index += 1
        if not p.mixer.music.get_busy():
            update_window_title("stopped")
            update_play_button("play_button")
            if auto_switch:
                play_Audio(track_list, track_list_index)
                auto_switch = False
        else:
            play_Audio(track_list, track_list_index)
    except IndexError:
        if not p.mixer.music.get_busy():        
            track_list_index = 0
            update_play_button("play_button")
            update_window_title("stopped")
        else:
            track_list_index = 0
            play_Audio(track_list, track_list_index)
        auto_switch = False
    except p.error as e:
        raise_Error(f"Error while loading track\n{e}", "Error")
        return

def previous_Track(track_list):
    global track_list_index
    
    try:
        track_list_index -= 1
        if track_list_index < 0:
            track_list_index = len(track_list) - 1
        if not p.mixer.music.get_busy():
            update_window_title("stopped")
            update_play_button("play_button")
        else:
            play_Audio(track_list, track_list_index)
    except p.error as e:
        raise_Error(f"Error while loading track\n{e}", "Error")
        return

def stop_Audio():
    global manual_stop
    global progress_bar

    try:
        p.mixer.music.stop()
        manual_stop = True
        update_play_button("play_button")
        update_window_title("stopped")
        progress_bar["value"] = 0
    except p.error as e:
        raise_Error(f"Error while stopping audio;\n{e}", "Error")
        return

def set_Volume(var):
    global volume

    volume = get_volume(var)
    
    try:
        p.mixer.music.set_volume(get_volume(var))
    except p.error as e:
        raise_Error(f"Error while updating volume;\n{e}", "Error")
        return

def import_Audio():
    global file_path
    global track_list
    global track_list_index

    file_path = filedialog.askopenfilenames(title="Open Audio Files")
    if file_path:
        if track_list:
            track_list.extend(list(file_path))
            for file in track_list:
                if track_list.count(file) >= 2:
                    track_list.remove(file)

            add_tracks_treeview()
        else:
            track_list = list(file_path)
            track_list_index = 0
            update_layout()
    else:
        raise_Error("No files have been selected;", "Warning", type="warning")

def update_play_button(button=""):
    if button == "pause_button":
        play_button.config(text="Pause", command=pause_Audio)
    elif button == "play_button":
        play_button.config(text="Play", command=lambda: play_Audio(track_list, track_list_index))
    elif button == "resume_button":
        play_button.config(text="Resume", command=unpause_Audio)

def update_window_title(status=""):
    if status == "stopped":
        window.title(f"Selected Track: {os.path.basename(track_list[track_list_index])} - Music Player")
    elif status == "playing":
        window.title(f"Playing {os.path.basename(track_list[track_list_index])} - Music Player")
    elif status == "default":
        window.title("Music Player")

def get_track_length(file_path):
    audio = File(file_path)
    if audio is None:
        return
    duration = audio.info.length

    return duration

def format_length(length):
    minutes, seconds = divmod(length, 60)

    formatted_length = f"{int(minutes)}:{int(seconds):02d}"
    return formatted_length

def add_tracks_treeview():
    global visual_track_list
    global existing_tracks

    existing_tracks = set()

    if visual_track_list:
        for item in visual_track_list.get_children():
            existing_tracks.add(visual_track_list.item(item, "values")[0])

    for track in track_list:
        title = os.path.basename(track)
        duration = format_length(get_track_length(track))
        
        if title not in existing_tracks:
            visual_track_list.insert("", tk.END, values=(title, duration))
            existing_tracks.add(title)

def get_volume(var):
    return float(var) / 100

def update_layout():
    global play_button
    global next_button
    global stop_button
    global visual_track_list
    global progress_bar
    global slider
    global volume
    global menu
    global playback_menu

    # Adjust layout
    import_text.config(text="Audio Imported Successfully!")

    play_button = ttk.Button(window, text="Play", command=lambda: play_Audio(track_list, track_list_index)) # Use lambda
    stop_button = ttk.Button(window, text="Stop", command=lambda: stop_Audio()) # add function here
    next_button = ttk.Button(window, text="Next", command=lambda: next_Track(track_list)) # Use print as a placeholder for functions
    previous_button = ttk.Button(window, text="Previous", command=lambda: previous_Track(track_list))

    tree_frame = ttk.Frame(window)
    tree_frame.place(x=window.winfo_width() / 7, y=35, height=350)

    visual_track_list = ttk.Treeview(tree_frame, columns=("Title", "Duration"), show="headings")
    visual_track_list.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

    visual_track_list.heading("Title", text="Title")
    visual_track_list.heading("Duration", text="Duration")

    visual_track_list.column("Title", width=250)
    visual_track_list.column("Duration", width=200)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=visual_track_list.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    visual_track_list.configure(yscrollcommand=scrollbar.set)

    add_tracks_treeview()

    progress_bar = ttk.Progressbar(window, orient="horizontal", length=500, mode="determinate")
    progress_bar.pack()

    slider = ttk.Scale(window, orient=tk.HORIZONTAL, from_=0, to=100, value=50, variable=volume, command=set_Volume)
    slider.pack()

    play_button.pack()
    stop_button.pack()
    next_button.pack()
    previous_button.pack()

    play_button.place(x=90, y=400, width=55)
    stop_button.place(x=190, y=400, width=35)
    previous_button.place(x=20, y=400, width=65)
    next_button.place(x=150, y=400, width=35)

    progress_bar.place(x=20, y=440)
    slider.place(x=530, y=440)

    visual_track_list.bind("<Double-1>", play_custom_Track)

def initialize_progress_bar(current_track):
    global progress_bar

    progress_bar.config(maximum=get_track_length(current_track))

    update_progress_bar()

def update_progress_bar():
    global progress_bar
    
    if p.mixer.music.get_busy() and not manual_stop:
        current_pos = p.mixer.music.get_pos() / 1000
        progress_bar["value"] = current_pos

        window.after(1000, update_progress_bar)

def check_for_track_end():
    global auto_switch
    
    if not p.mixer.music.get_busy() and not manual_stop:
        auto_switch = True
        next_Track(track_list)
        return
    else:
        window.after(1000, check_for_track_end)

def layout():
    global window
    global import_text
    global file_menu
    global menu

    window = tk.Tk()
    window.geometry("640x480")
    window.resizable(False, False)

    window.title("Music Player")

    import_text = tk.Label(window, text="Import Audio.")
    import_text.pack()

    menu = tk.Menu(window)

    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label="Open", command=import_Audio)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.quit)

    menu.add_cascade(label="File", menu=file_menu)
    
    window.config(menu=menu)

    window.mainloop()

layout()