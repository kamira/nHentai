# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import yaml
import os
import re
import logging
from multiprocessing import Pool
import random
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from downloader_mp import download_start
from functools import partial


class Window(Frame):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        self.master = master



class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, record):
        # Append message (record) to the widget
        self.widget.insert(END, record + '\n')
        self.widget.update()



def main():
    def download_button_click():
        end = end_value.get()
        start = start_value.get()
        path = path_value.get()
        if end.isdigit() and start.isdigit():
            end = int(end)
            start = int(start)
            if end > start:
                sct.emit("Information------\n" +
                                        "{:>10} : {:<5}\n".format("Start", start) +
                                        "{:>10} : {:<5}\n".format("End", end) +
                                        "{:>10} : {}\n".format("Path", path))
                # print(sct)
                download_start(start, end, path)
                sct.emit("[Finish] {} - {} \n Filepath: {}\n".format(start, end, path))
            else:
                sct.emit("[ERROR] end should bigger than start\n")
        else:
            sct.emit("[ERROR] start or end id isn't a digital number\n")
    root = Tk()
    app = Window(root)
    root.title("nHentai Downloader")

    id_select_frame = Frame(root)
    id_select_frame.grid(row=0, column=0)
    start_label = Label(id_select_frame, text='Start')
    start_label.grid(row=0, column=0, sticky=E, pady=2)
    start_value = StringVar()
    start_entry = Entry(id_select_frame, textvariable=start_value)
    start_entry.grid(row=0, column=1)

    end_label = Label(id_select_frame, text='End')
    end_label.grid(row=1, column=0, sticky=E, pady=2)
    end_value = StringVar()
    end_entry = Entry(id_select_frame, textvariable=end_value)
    end_entry.grid(row=1, column=1)
    path_label = Label(id_select_frame, text='Download Path')
    path_label.grid(row=3, column=0, columnspan=2, pady=10)
    path_value = StringVar()
    path_value.set(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download'))
    path_entry = Entry(id_select_frame, textvariable=path_value)
    path_entry.grid(row=4, columnspan=2, sticky="WE")

    start_button = Button(id_select_frame, text="Start Download", command=download_button_click)
    start_button.grid(row=6, columnspan=2, sticky="WE", padx=10, pady=10)

    log_frame = Frame(root)
    log_frame.grid(row=0, column=1)
    scroll_text = ScrolledText(log_frame, wrap=WORD)
    scroll_text.grid()
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s - %(message)s')
    sct = WidgetLogger(scroll_text)
    root.mainloop()
    pass

if __name__ == '__main__':
    main()









