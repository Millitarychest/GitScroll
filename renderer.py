import os
import sys
import shutil
from Mdparser import parseMD, Markdown, Image, CodeBlock ,Paragraph, Link, List, Text, Emphasis, Bold, Header
from html import escape

def render(markdown):
    if not isinstance(markdown, Markdown):
        return
    html = '<head>\n\t<link rel="stylesheet" href="prism.css">\n<link rel="stylesheet" href="darkStyle.css">\n</head>\n<body>\n'
    for block in markdown.blocks:
        if isinstance(block, Paragraph):
            html += render_paragraph(block)
        elif isinstance(block, List):
            html += render_list(block)
        elif isinstance(block, CodeBlock):
            html += render_codeblock(block)
        elif isinstance(block, Image):
            html += render_image(block)
        elif isinstance(block, List):
            html += render_list(block, in_list=True)
        else:
            raise TypeError('Unknown block {!r}'.format(block))
    html += '</body>\n<script src="prism.js"></script>'
    return html

def render_image(block):
    try:
        moveImage(block.url)
    except:
        pass
    return '<img src="%s" alt="%s">' % (block.url, block.alt)

def moveImage(file):
    shutil.copy(file, "./out/" + file)

def render_paragraph(paragraph, in_list=False):
    html = ''
    for item in paragraph.items:
        if isinstance(item, Text):
            html += render_text(item)
        elif isinstance(item, List):
            html += render_list(item, in_list)
        elif isinstance(item, Header):
            html += render_header(item)
        elif isinstance(item, Emphasis):
            html += render_emphasis(item)
        elif isinstance(item, Bold):
            html += render_bold(item)
        elif isinstance(item, Link):
            html += render_link(item)
        elif isinstance(item, Image):
            html += render_image(item)
        else:
            raise TypeError('Unknown block {!r}'.format(paragraph))
    return html if in_list else '<p>%s</p>\n' % html


def render_link(link):
    return '<a href="%s">%s</a>' % (link.url, link.text)

def render_codeblock(codeblock):
    return '<pre><code class="language-%s">%s</code></pre>' % (codeblock.language ,escape(codeblock.code))

def render_list(l, in_list=False, indent_level=0):
    html = ''
    indent = '\t' * indent_level  # Indentation based on the current level

    if not in_list:
        html += indent + '<ul>\n'  # Start of the outermost <ul> tag

    if isinstance(l, List):
        items = l.items if isinstance(l.items, list) else [l.items]  # Ensure items is always a list
        
        for item in items:

            if isinstance(item, List):
                subindent = '\t' * (indent_level + 1)  # Indentation for nested lists
                html += subindent + '<ul>\n'
                html += render_list(item, in_list=True, indent_level=indent_level + 1)  # Recursive call for nested lists
                html += subindent + '</ul>\n'
            else:
                html += indent + '\t<li>\n' + indent + '\t\t' + render_item(item) + '\n' + indent + '\t</li>\n'

    if not in_list:
        html += indent + '</ul>\n'  # End of the outermost <ul> tag

    return html


def render_item(item):
    if isinstance(item, Paragraph):
        return render_paragraph(item, in_list=True)
    elif isinstance(item, Link):
        return render_link(item)
    else:
        raise TypeError('Unknown item {!r}'.format(item))






def render_header(header):
    level = header.level
    html = ''
    for item in header.items:
        if isinstance(item, Emphasis):
            emphasis = render_emphasis(item)
            html += emphasis
        if isinstance(item, Bold):
            bold = render_bold(item)
            html += bold
        else:  # item is Text
            html += render_text(item)
    if(level > 1):
        return '\n<h%d>%s</h%d>\n' % (level, html, level)
    else:
        return '\n<h%d>%s</h%d>\n<hr>' % (level, html, level)


def render_emphasis(emphasis):
    return '<em>%s</em>' % (emphasis.text)


def render_bold(bold):
    return '<b>%s</b>' % (bold.text)


def render_text(text):
    return text.text




def encfile(filename, pw):
    # Encrypt file
    print("staticrypt %s -p %s -d ./out --short" % (filename, pw))
    os.system("staticrypt %s -p %s -d ./out --short" % (filename, pw))

def codeStyling():
    # Code styling
    shutil.copyfile("./utils/darkStyle.css", "./out/darkStyle.css")
    shutil.copyfile("./utils/prism_dark.css", "./out/prism.css")
    shutil.copyfile("./utils/prism_dark.js", "./out/prism.js")



def mark(MdFile):
    try:
        pw = ""
        filename = MdFile
        dePathedFilename = filename.replace("./in/", "")

        with open(filename, 'r') as f:
            rawMD = f.readlines()
            if rawMD[0].startswith("password:"):
                pw = rawMD[0].split(":")[1].strip()
                
                rawMD = rawMD[1:]
            rawMD = ''.join(rawMD)
            markdown = parseMD(rawMD)
            with open('./out/%s.html' % dePathedFilename.split('.')[0], 'w') as html_f:
                html_f.write(render(markdown))
            if pw != "":
                encfile('./out/%s.html' % dePathedFilename.split('.')[0], pw)
            codeStyling()



    except:
        pass




# renderer test calls
if __name__ == '__main__':
    try:
        pw = ""
        filename = sys.argv[1]
        with open(filename, 'r') as f:
            rawMD = f.readlines()
            if rawMD[0].startswith("password:"):
                pw = rawMD[0].split(":")[1].strip()
                rawMD = rawMD[1:]
            rawMD = ''.join(rawMD)
            markdown = parseMD(rawMD)
            with open('./out/%s.html' % filename.split('.')[0], 'w') as html_f:
                html_f.write(render(markdown))
            if pw != "":
                encfile('./out/%s.html' % filename.split('.')[0], pw)
            codeStyling()



    except IOError:
        print ("File not found")