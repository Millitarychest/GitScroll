from flask import Flask, render_template
from gitscroll import get_index


app = Flask(__name__,
            static_url_path='', 
            static_folder='out',
            template_folder='out')

@app.route("/")
def blog():
    return render_template(get_index("./in/")[0].link.replace(".md", ".html"))

@app.route("/edit")
def editor():
    return render_template('PLACEHOLDER.html')

if __name__ == '__main__':
    app.run(debug=True)