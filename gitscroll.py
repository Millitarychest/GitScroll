import subprocess

def encfile(filename, pw):
    # Encrypt file
    Htfilename = filename.split(".")[0] + ".html"
    subprocess.run(["staticrypt",filename, pw ,"-o", Htfilename])