from app import db, login_manager, bcrypt, create_app
from flask import (Flask,render_template,redirect,flash,url_for,session,request)
from models import User
from sqlalchemy.exc import (IntegrityError,DataError,DatabaseError,InterfaceError,InvalidRequestError,)
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from forms import login_form, register_form
from gitscroll import get_index, generateEditIndexComponent, company, startup
import gitHelper
import argparse
import os

#globals
arg_file = None

arg_port = 5000
arg_debug = True
arg_input = "./in/"
arg_output = "./out/"
arg_company = "GitScroll"
arg_tmp = "./tmp/"
arg_gitWeb = None

app = create_app()


#auth stuff
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#web routes
@app.route("/")
def blog():
    return render_template("blog/" + getIndexLink())


@app.route("/edit", methods =["GET", "POST"])
@login_required
def editor():
    if request.method == "POST":
        if request.args.get('site'):
            save_file(request.args.get('site'), request.form.get('content').replace("\r", ""))
    text = "An editor for your blog!"
    if request.args.get('site'):
        text = load_file(request.args.get('site'))
    return render_template('editor/edit.html', Index=set_index(), Content=text, Title=arg_company)

@app.route("/add", methods =["GET", "POST"])
@login_required
def addEditor():
    if request.method == "POST":
        save_file(request.form.get('file').replace("\r", "") + ".md", request.form.get('content').replace("\r", ""))
        return redirect("/edit?site=" + request.form.get('file').replace("\r", "") + ".md")
    text = "HI!!"
    return render_template('editor/add.html', Index=set_index(), Content=text, Title=arg_company)

#auth routes

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect("/edit")
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        Title=arg_company,
        btn_action="Login"
        )

@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )






#helper functions
def getIndexLink():
    sections = get_index(arg_input)
    for section in sections:
        if section.link.endswith(".md"):
            return section.link.replace(".md", ".html")

def load_file(path):
    try:
        base = os.path.realpath(arg_input)
        cleanPath = os.path.realpath(arg_input + path)
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
        base = os.path.realpath(arg_input)
        cleanPath = os.path.realpath(arg_input + path)
        prefix = os.path.commonpath([base, cleanPath])
        if prefix == base:
            with open(arg_input+path, 'w') as f:
                return f.write(content)
        return "File not found"
    except:
        print("File not found")
        return "File not found"

def set_index():
    links = []
    ind = get_index(arg_input)
    links = generateEditIndexComponent(ind)
    return links



if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='GitScroll Markdown Blog with web editor')
    #flask args
    flaskParams = argparser.add_argument_group('flask parameters')
    flaskParams.add_argument('-p', '--port', help='Port to run on', default=arg_port, type=int)
    flaskParams.add_argument('-d', '--debug', help='Debug mode', default=False, action='store_true')

    #gitscroll args
    gitScrollParams = argparser.add_argument_group('gitscroll parameters')
    gitScrollParams.add_argument('-c', '--company', help='Company name', default=arg_company)
    gitScrollParams.add_argument('-i', '--input', help='input folder', default=arg_input)
    gitScrollParams.add_argument('-o', '--output', help='output folder', default=arg_output)
    gitScrollParams.add_argument('-t', '--tmp', help='tmp folder', default=arg_tmp)

    #git args
    gitParams = argparser.add_argument_group('git parameters')
    gitParams.add_argument('--gitURL', help='git repo url for setup', default=arg_gitWeb)


    args = argparser.parse_args()
    arg_debug = args.debug
    arg_port = args.port
    arg_input = args.input
    arg_output = args.output
    arg_company = args.company
    arg_tmp = args.tmp
    arg_gitWeb = args.gitURL

    #setup git repo if needed
    print(">Setting up git repo")
    if not (os.path.exists(arg_input + ".git") or os.path.exists(arg_input + "/.git")):
        if arg_gitWeb:
            gitHelper.setup_from_remote(arg_gitWeb, arg_input)
    
    elif (os.path.exists(arg_input + ".git") or os.path.exists(arg_input + "/.git")) and arg_gitWeb:
        gitHelper.update(arg_input)

    elif os.path.exists(arg_input + ".git") or os.path.exists(arg_input + "/.git"):
        print("Git repo already setup")
        print("Updating repo")
        gitHelper.update(arg_input)
    #run markdown parser
    startup(arg_input, arg_output, arg_tmp, arg_company)
    #run web app
    print(">Running web editor")
    app.run(debug=arg_debug, port=arg_port)