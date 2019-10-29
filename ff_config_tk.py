# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 07:44:06 2019

@author: buriona
"""

from tkinter import Tk, Button
from tkinter.ttk import Combobox
from hdb_api.hdb_utils import get_eng_config
from hdb_api.hdb_api import Hdb, HdbTables

def get_meta(hdb_alias):
    

window = Tk()
 
window.title("Welcome to LikeGeeks app")
 
window.geometry('350x200')
 
combo = Combobox(window)
 
combo['values']= ('UC', 'LC', 'ECO', 'LBO', 'YAO')
 
combo.current(0)
 
combo.grid(column=0, row=0)
 
btn = Button(window, text="Click Me", command=get_meta)
 
btn.grid(column=2, row=0)
 

window.mainloop()