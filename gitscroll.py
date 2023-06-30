from renderer import render, encfile, codeStyling, render_in_subdir
from templater import template_set, template_load_set
from Mdparser import parseMD
import os

dir = "./in/"
company = "Company"
ignore = []
index = []
'''
index[chapter[section[]],chapter[section[child[]]],chapter[]]
==>
chapter =drop down=> section 

chapter =drop down=> section =drop down=> child

chapter
'''

class Section(object):
    def __init__(self, name, link, children, depth=0):
        self.name = name
        self.link = link
        self.children = children
        self.depth = depth

    def __repr__(self):
        return 'Section({!r})({})'.format(self.name, self.children)

def get_index(directory, depth=0):
    ind = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            if filename not in ignore:
                if ((directory + filename).replace("./in/","",1) not in ignore):
                    ind.append(Section(filename.replace(".md", ""), (directory+filename).replace("./in/","",1) ,[]))
        elif os.path.isdir(directory +filename):
            ind.append(Section(filename.replace(".md", ""),(directory + filename).replace("./in/","",1) ,get_index(directory + filename + "/", depth+1), depth))
    return ind            


def convert(directory):
    for filename in os.listdir(directory):
        
        if filename.endswith(".md"):
            if filename not in ignore:
                if ((directory + filename).replace("./in/","",1) not in ignore):
                    mark(directory + filename)
        elif os.path.isdir(directory +filename):
            convert(directory + filename + "/")

def loadIgnore(directory):
    ig = []
    with open(directory + ".scrollignore", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("*"):
                ig.append(line.replace("*", "").replace("\n", ""))
            else:
                ig.append(line.replace("\n", ""))
    return ig

def mark(MdFile):
    try:
        pw = ""
        filename = MdFile
        dePathedFilename = filename.replace("./in/", "")
        #print(dePathedFilename)
        with open(filename, 'r') as f:
            rawMD = f.readlines()
            if rawMD[0].startswith("password:"):
                pw = rawMD[0].split(":")[1].strip()
                rawMD = rawMD[1:]
            rawMD = ''.join(rawMD)
            markdown = parseMD(rawMD)
            ##call templater to generate final blog
            subdirs = dePathedFilename.split('/')
            subdirs.pop()
            if len(subdirs) > 0:
                if not os.path.exists("./out/" + "/".join(subdirs)):
                    os.makedirs("./out/" + "/".join(subdirs))
            with open('./out/%s.html' % dePathedFilename.split('.')[0], 'w') as html_f:
                #print("writing to " + './out/%s.html' % dePathedFilename.split('.')[0])
                if len(subdirs) < 1:
                    html_f.write(template_set("Title", company, template_set("Index", generateIndexComponent(index) ,template_load_set('Content', render(markdown), './utils/template/template.html'))))
                else:
                    html_f.write(template_set("Title", company, template_set("Index", generateIndexComponent(index, len(subdirs)) ,template_load_set('Content', render_in_subdir(markdown, subdirs), './utils/template/template.html'))))
            if pw != "":
                encfile('./out/%s.html' % dePathedFilename.split('.')[0], pw)
            codeStyling()
    except Exception as e:
        print(e)

def hasSummary(directory):
    for filename in os.listdir("./in/"+directory):
        if filename == "SUMMARY.md":
            return True
    return False

def generateIndexComponent(index, depth=0):
    def generateSectionLinks(sections, depth=0):
        links = []
        for section in sections:
            if section.children:
                dotDeep = depth - section.depth
                if dotDeep < 0:
                    dotDeep = 0
                dots = "../" * dotDeep
                if hasSummary(section.link):
                    links.append(('<details id="'+ section.name +'" open>\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        "<a href='"+ dots +section.link + "/SUMMARY.html#" + section.name + "'>" +section.name + "</a>", generateSectionLinks(section.children, depth)))
                else:
                    links.append(('<details id="'+ section.name +'" open>\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        section.name, generateSectionLinks(section.children, depth)))
            else:
                if section.name != "SUMMARY":
                    dotDeep = depth
                    if dotDeep < 0:
                        dotDeep = 0
                    dots = "../" * dotDeep
                    links.append('<li><a href="./{}">{}</a></li>'.format(dots + section.link.replace(".md", ".html"), section.name))
        return '\n'.join(links)

    return generateSectionLinks(index, depth)


ignore = loadIgnore(dir)
index = get_index(dir)
convert(dir)