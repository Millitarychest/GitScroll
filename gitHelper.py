import os
import shlex

def update(path):
    os.system("git -C " + shlex.quote(path) + " pull")

def setup_from_remote(url, path):
    url = shlex.quote(url)
    os.system("git clone " + url + " " + shlex.quote(path))

def setup_local(path, remote):
    remote = shlex.quote(remote)
    path = shlex.quote(path)
    os.system("git -C " + path + " init")
    os.system("git -C " + path + " add .")
    os.system("git -C " + path + " commit -m \"Initial commit\"")
    os.system("git -C " + path + " branch -M main")
    os.system("git -C " + path + " remote add origin" + remote)
    os.system("git -C " + path + " push -u origin main")

def push(path):
    path = shlex.quote(path)
    os.system("git -C " + path + " add .")
    os.system("git -C " + path + " commit -m \"Blog Update\"")
    os.system("git -C " + path + " push -u origin main")

