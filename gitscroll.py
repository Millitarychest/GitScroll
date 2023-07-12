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
    def __init__(self, name, link, children, depth=0):
        self.name = name
        self.link = link
        self.children = children
        self.depth = depth

    def __repr__(self):
        return 'Section({!r})({})'.format(self.name, self.children)

def get_index(directory, depth=0):
    ignore = loadIgnore(dir)
    ind = []
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                    ind.append(Section(filename.replace(".md", ""), (directory+filename).replace(dir,"",1) ,[]))
        elif os.path.isdir(directory +filename):
            if filename not in ignore:
                if ((directory + filename).replace(dir,"",1) not in ignore):
                        ind.append(Section(filename.replace(".md", ""),(directory + filename).replace(dir,"",1) ,get_index(directory + filename + "/", depth+1), depth))
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

def mark(MdFile):
    try:
        pw = ""
        filename = MdFile
        deInPathedFilename = filename.replace(dir, "")
        dePathedFile = deInPathedFilename.split("/")[-1]
        #print(deInPathedFilename)
        with open(filename, 'r') as f:
            rawMD = f.readlines()
            if rawMD[0].startswith("password:"):
                pw = rawMD[0].split(":")[1].strip()
                rawMD = rawMD[1:]
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
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index, len(subdirs)) ,staticTemplater.template_load_set('Content', render_in_subdir(markdown, dir, outdir, tmpDir, subdirs), './utils/template/template.html'))))
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
                        html_f.write(staticTemplater.template_set("Title", company, staticTemplater.template_set("Index", generateIndexComponent(index, len(subdirs)) ,staticTemplater.template_load_set('Content', enc_file, './utils/template/template_framed.html'))))

            codeStyling()
    except Exception as e:
        print(e)

def hasSummary(directory):
    for filename in os.listdir(dir+directory):
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
                        "<a href='/"+section.link + "/SUMMARY.html'>" +section.name + "</a>", generateSectionLinks(section.children, depth)))
                else:
                    links.append(('<details id="'+ section.name +'" open>\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        section.name, generateSectionLinks(section.children, depth)))
            else:
                if section.name != "SUMMARY":
                    dotDeep = depth
                    if dotDeep < 0:
                        dotDeep = 0
                    dots = "../" * dotDeep
                    links.append('<li><a href="/{}">{}</a></li>'.format(section.link.replace(".md", ".html"), section.name))
        return '\n'.join(links)

    return generateSectionLinks(index, depth)

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
                    links.append(('<details id="'+ section.name +'" open>\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        "<a href='/edit?site="+ dots +section.link + "/SUMMARY.md'>" +section.name + "</a>", generateEditSectionLinks(section.children, depth)))
                else:
                    links.append(('<details id="'+ section.name +'" open>\n<summary>{}</summary>\n<ul>\n{}\n</ul>\n</details>').format(
                        section.name, generateEditSectionLinks(section.children, depth)))
            else:
                if section.name != "SUMMARY":
                    dotDeep = depth
                    if dotDeep < 0:
                        dotDeep = 0
                    dots = "../" * dotDeep
                    links.append('<li><a href="/edit?site={}">{}</a></li>'.format(dots + section.link, section.name))
        return '\n'.join(links)

    return generateEditSectionLinks(index, depth) + '<li><a href="/add">{}</a></li>'.format( "Add new post")

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