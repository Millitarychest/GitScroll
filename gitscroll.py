from renderer import render, encfile, codeStyling, render_in_subdir, moveRes
from templater import staticTemplater
from Mdparser import parseMD
import os
import shutil

dir = "./in/"
outdir = "./out/"
tmpDir = "./tmp/"
company = "GitScroll"
ignore = []
index = []

class Section(object):
    def __init__(self, name, link, children, depth=0, order=None):
        self.name = name
        self.link = link
        self.children = children
        self.depth = depth
        self.order = order

    def __repr__(self):
        return 'Section({!r})({})'.format(self.name, self.children)

def get_index(directory, depth=0):
    ignore = loadIgnore(dir)
    ind = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                    ind.append(Section(filename.replace(".md", ""), (directory+filename).replace(dir,"",1) ,[], order=checkForScrollPos(directory + filename)))
        elif os.path.isdir(directory +filename):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                        ind.append(Section(filename.replace(".md", ""),(directory + filename).replace(dir,"",1) ,get_index(directory + filename + "/", depth+1), depth))
    ind = sortbyOrder(ind)
    return ind            




def convert(directory):
    
    for filename in os.listdir(directory):
        
        if filename.endswith(".md"):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                    mark(directory + filename)
                else:
                    print("Ignoring file " + filename)
            else:
                print("Ignoring file " + filename)
        elif os.path.isdir(directory +filename):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                    convert(directory + filename + "/")
                else:
                    print("Ignoring folder " + filename)
            else:
                print("Ignoring folder " + filename)

def checkForScrollPos(file):
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("<-->pos:") or line.startswith("<-->position:"):
                return line.split(":")[1].strip().replace("<-->", "")

def loadIgnore(directory):
    ig = []
    with open(directory + ".scrollignore", "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("*"):
                ig.append(line.replace("*", "").replace("\n", "")) #if * is at the start of the line, ignore the file everywhere
            else:
                ig.append(line.replace("\n", "")) # else ignore only if exact path is matched
    return ig

def checkForScrollFunc(raws, file, mark=False):
    pw = ""
    newRaws = []
    for raw in raws:
        if raw.startswith("<-->password:") and mark: #pw set in <-->password:password<-->
            pw = raw.split(":")[1].strip().replace("<-->", "")
        elif raw.startswith("<-->pos:") or raw.startswith("<-->position:"): #pos set in <-->pos:position<-->
            pass    
        else:
            newRaws.append(raw)
    newRaws.append(pw)
    return newRaws

def mark(MdFile):
    try:
        pw = ""
        filename = MdFile
        deInPathedFilename = filename.replace(dir, "")
        dePathedFile = deInPathedFilename.split("/")[-1]
        #print(deInPathedFilename)
        with open(filename, 'r') as f:
            rawMD = f.readlines()
            rawMD = checkForScrollFunc(rawMD, deInPathedFilename, True)
            #get password if exists
            pw = rawMD[-1]
            rawMD = rawMD[:-1]

            if not next((s for s in rawMD if s), filename).startswith("#"):
                rawMD.insert(0, "# " + dePathedFile.replace(".md", "") + "\n\n")
            rawMD = ''.join(rawMD)
            markdown = parseMD(rawMD)
            ##call templater to generate final blog
            subdirs = deInPathedFilename.split('/')
            subdirs.pop()
            if len(subdirs) > 0:
                if not os.path.exists(outdir + "/".join(subdirs)):
                    os.makedirs(outdir + "/".join(subdirs))
            if pw == "":
                with open(outdir + '%s.html' % deInPathedFilename.split('.')[0], 'w') as html_f:
                    #print("writing to " + './out/%s.html' % deInPathedFilename.split('.')[0])
                    if len(subdirs) < 1:
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index) ,staticTemplater.template_load_set('Content', render(markdown, dir, outdir, tmpDir), './utils/template/template.html'))))
                    else:
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index) ,staticTemplater.template_load_set('Content', render_in_subdir(markdown, dir, outdir, tmpDir, subdirs), './utils/template/template.html'))))
            if pw != "":
                with open(tmpDir + '%s.html' % deInPathedFilename.split('.')[0], 'w') as html_f:
                    #print("writing to " + './out/%s.html' % deInPathedFilename.split('.')[0])
                    if len(subdirs) < 1:
                        html_f.write(render(markdown, dir, outdir, tmpDir))
                    else:
                        html_f.write(render_in_subdir(markdown, dir, outdir, tmpDir, subdirs))
                encfile(tmpDir + '%s.html' % deInPathedFilename.split('.')[0], pw)
                enc_file = moveRes(tmpDir + '%s.html' % deInPathedFilename.split('.')[0], '%s_enc.html' % deInPathedFilename.split('.')[0] )
                with open(outdir + '%s.html' % deInPathedFilename.split('.')[0], 'w') as html_f:
                    #print("writing to " + './out/%s.html' % deInPathedFilename.split('.')[0])
                    if len(subdirs) < 1:
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index) ,staticTemplater.template_load_set('Content', enc_file, './utils/template/template_framed.html'))))
                    else:
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index) ,staticTemplater.template_load_set('Content', enc_file, './utils/template/template_framed.html'))))

            codeStyling()
    except Exception as e:
        print(e)

def hasSummary(directory):
    for filename in os.listdir(dir+directory):
        if filename == "SUMMARY.md":
            return True
    return False

def sortbyOrder(sections):
    toOrder = []
    noOrder = []
    for section in sections:
        if section.order is not None:
            toOrder.append(section)
        else:
            noOrder.append(section)

    # Sort sections that have order assigned
    toOrder.sort(key=lambda x: x.order)

    # Recursively sort sections in subdirectories
    for section in toOrder:
        if section.children:
            section.children = sortbyOrder(section.children)

    # Combine sections with order and sections without order
    orderedSections = toOrder + noOrder

    return orderedSections

def generateIndexComponent(index):
    def generateSectionLinks(sections):
        links = []
        for section in sections:
            if section.children:
                if hasSummary(section.link):
                    links.append(('<details id="'+ section.name +'" >\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        "<a href='/"+section.link + "/SUMMARY.html'>" +section.name + "</a>", '\n'.join(generateSectionLinks(section.children))))  # Increase depth for subdirectories
                else:
                    links.append(('<details id="'+ section.name +'" >\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        section.name, '\n'.join(generateSectionLinks(section.children))))  # Increase depth for subdirectories
            else:
                if section.name != "SUMMARY":
                    links.append('<li><a id="{}" href="/{}">{}</a></li>'.format(section.name ,section.link.replace(".md", ".html"), section.name))
        return links

    nav = generateSectionLinks(index)
    
    return '\n'.join(nav)


def generateEditIndexComponent(index, depth=0):
    def generateEditSectionLinks(sections, depth=0):
        links = []
        for section in sections:
            if section.children:
                dotDeep = depth - section.depth
                if dotDeep < 0:
                    dotDeep = 0
                dots = "../" * dotDeep
                if hasSummary(section.link):
                    links.append(('<details id="'+ section.name +'" >\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        "<a id='" + dots + section.link + "/SUMMARY.md' href='/edit?site="+ dots +section.link + "/SUMMARY.md'>" +section.name + "</a>", '\n'.join(generateEditSectionLinks(section.children, depth))))
                else:
                    links.append(('<details id="'+ section.name +'" >\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        section.name, '\n'.join(generateEditSectionLinks(section.children, depth))))
            else:
                if section.name != "SUMMARY":
                    dotDeep = depth
                    if dotDeep < 0:
                        dotDeep = 0
                    dots = "../" * dotDeep
                    links.append('<li><a id="{}" href="/edit?site={}">{}</a></li>'.format(dots + section.link ,dots + section.link, section.name))
        return links
    
    nav = '\n'.join(generateEditSectionLinks(index, depth))
    return nav + '<li id="add-post"><a  href="/add">{}</a></li>'.format( "Add new post")

def cleanup():
    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir)
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(tmpDir)
    os.makedirs(outdir)

def cleanupTmp():
    if os.path.exists(tmpDir):
        shutil.rmtree(tmpDir)
    os.makedirs(tmpDir)

def startup(input, output, tmp, title):
    #set globals
    global dir
    global outdir
    global tmpDir
    global company
    dir = input
    outdir = output
    tmpDir = tmp
    company = title

    #prep
    cleanup()
    global ignore
    global index
    ignore = loadIgnore(dir)
    index = get_index(dir)
    #parse
    print(">Converting files")
    convert(dir)
    cleanupTmp()

if __name__ == "__main__":
    cleanup()
    ignore = loadIgnore(dir)
    index = get_index(dir)
    print(">Converting files")
    convert(dir)
    cleanupTmp()