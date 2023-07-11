import os
from flask import Flask, redirect, render_template, request
from gitscroll import get_index, generateEditIndexComponent, company, startup


app = Flask(__name__, static_url_path='', static_folder='templates/blog')

@app.route("/")
def blog():
    return render_template("blog/" + getIndexLink())

@app.route("/edit", methods =["GET", "POST"])
def editor():
    if request.method == "POST":
        if request.args.get('site'):
            save_file(request.args.get('site'), request.form.get('content').replace("\r", ""))
    text = "An editor for your blog!"
    if request.args.get('site'):
        text = load_file(request.args.get('site'))
    return render_template('editor/edit.html', Index=set_index(), Content=text, Title=company)

@app.route("/add", methods =["GET", "POST"])
def addEditor():
    if request.method == "POST":
        save_file(request.form.get('file').replace("\r", "") + ".md", request.form.get('content').replace("\r", ""))
        return redirect("/edit?site=" + request.form.get('file').replace("\r", "") + ".md")
    text = "HI!!"
    return render_template('editor/add.html', Index=set_index(), Content=text, Title=company)

def getIndexLink():
    sections = get_index("./in/")
    for section in sections:
        if section.link.endswith(".md"):
            return section.link.replace(".md", ".html")

def load_file(path):
    try:
        base = os.path.realpath("./in/")
        cleanPath = os.path.realpath("./in/" + path)
        prefix = os.path.commonpath([base, cleanPath])
        if prefix == base:
            with open(cleanPath, 'r') as f:
                return f.read()
        return "File not found"
    except:
        print("File not found")
        return "File not found"
    

def save_file(path, content):
    try:
        base = os.path.realpath("./in/")
        cleanPath = os.path.realpath("./in/" + path)
        prefix = os.path.commonpath([base, cleanPath])
        if prefix == base:
            with open("./in/"+path, 'w') as f:
                return f.write(content)
        return "File not found"
    except:
        print("File not found")
        return "File not found"

def set_index():
    links = []
    ind = get_index("./in/")
    links = generateEditIndexComponent(ind)
    return links



if __name__ == '__main__':
    startup()
    app.run(debug=True)