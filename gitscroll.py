from renderer import mark
import os

directory = "./in/"


for filename in os.listdir(directory):
    
    if filename.endswith(".md"):
        mark(directory + filename)
    else:
        continue
