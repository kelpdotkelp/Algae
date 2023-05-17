import tkinter as tk

def create(frame_content_base):
    frame_page_base = tk.Frame(frame_content_base)

    tk.Label(frame_page_base, text='Hardware setup tab.').pack()

    return frame_page_base