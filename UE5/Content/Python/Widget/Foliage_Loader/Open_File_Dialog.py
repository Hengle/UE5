"""This script is part of python script node"""
import tkinter
from tkinter import filedialog
from unreal import Paths
from os import path

# Argument from node input
foliage_dir = directory
saved_dir = Paths.project_saved_dir()
foliage_path = f'{saved_dir}{foliage_dir}'
foliage_directory_exist = path.exists(foliage_path)
if not foliage_directory_exist:
    foliage_path = saved_dir
root = tkinter.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir=foliage_path)
