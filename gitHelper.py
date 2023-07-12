import os

def update(path):
    os.system("git -C " + path + " pull")

def setup_from_remote(url, path):
    os.system("git clone " + url + " " + path)

def setup_local(path, remote):
    os.system("git -C " + path + " init")
    os.system("git -C " + path + " add .")
    os.system("git -C " + path + " commit -m \"Initial commit\"")
    os.system("git -C " + path + " branch -M main")
    os.system("git -C " + path + " remote add origin" + remote)
    os.system("git -C " + path + " push -u origin main")

def push(path):
    os.system("git -C " + path + " add .")
    os.system("git -C " + path + " commit -m \"Blog Update\"")
    os.system("git -C " + path + " push -u origin main")

