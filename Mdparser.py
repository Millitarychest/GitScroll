import re


def parseMD(rawMD):
    #getBlocks
    #print( Markdown([parseBlock(block) for block in split_into_blocks(rawMD)]) )
    return Markdown([parseBlock(block) for block in split_into_blocks(rawMD)])

def split_into_blocks(string):
    return re.split(r'\n{2,}', string)

def parseBlock(block):
    #get headers
    block = findHeader(block)
    if not isinstance(block, str):
        for header in block.items:
            parts = re.split('(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)', header.items)
            header.items = list(map(parse_inlines, parts))
        return block
    #get lists
    match = re.match(r'^[-|\*]\s+', block)
    if match is not None:
        # '^' should match at the beginning of the string and at the beginning of each line
        items = [item.strip() for item in re.split(r'^[-|\*]\s+', block, flags=re.M)[1:]]  
        lists = List(list(map(parse_paragraph, items)))
        #print(lists.items[0].items[0])
        for item in lists.items:
            if not isinstance(item.items[0], Paragraph):
                match = re.search(r'\s+[-|\*]\s+', item.items[0].text)
                if match is not None:
                    inner_items = [inner_item.strip() for inner_item in re.split(r'\s+[-|\*]\s+', item.items[0].text, flags=re.M)]
                    item.items = list()
                    item.items.append(parse_paragraph(inner_items[0]))
                    inner_lists = List(map(parse_paragraph, inner_items[1:]))
                    item.items.append(inner_lists)
        return lists
    # get code blocks with lang
    match = re.match(r'^```(\w+)\n([\s\S]+?)\n```$', block, re.DOTALL)
    if match is not None:
        language = match.group(1)
        code = match.group(2)
        return CodeBlock(code, language)

    # get code blocks without language
    if block.startswith("```") and block.endswith("```"):
        code = block.strip("`\n")
        return CodeBlock(code)
    # get images
    match = re.match(r'^!\[([^\]]+)\]\(([^)]+)\)$', block)
    if match is not None:
        alt_text = match.group(1)
        image_url = match.group(2)
        return Image(alt_text, image_url)
    return parse_paragraph(block)

def parse_paragraph(block):
    inlines_regex = '(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*|!\\[[^\\]]+\\]\\([^\\)]+\\))'
    #inlines_regex = '(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)'
    parts = re.split(inlines_regex, block)  # split out Emphasis and Bold
    return Paragraph(list(map(parse_inlines, parts)))

def parse_inlines(string):
    '''Parse Emphasis and Bold
    '''
    for regexp, klass in INLINE_ELEMENTS:
        match = re.match(regexp, string)
        if match is not None:
            return klass(match.group(1))
    match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', string)
    if match is not None:
        alt_text = match.group(1)
        image_url = match.group(2)
        return Image(alt_text, image_url)
    return parseLink(string)

def parseCode(text):
    # ``` followed by anything but a newline, followed by ```	
    code_regex = r'```([^`]+)```'
    return text

def parseLink(text):
    # Anything that isn't a square closing bracket
    name_regex = "[^]]+"
    # http:// or https:// followed by anything but a closing paren
    url_regex = "http[s]?://[^)]+"

    markup_regex = '\[({0})]\(\s*({1})\s*\)'.format(name_regex, url_regex)

    linkPara = Paragraph(list())

    matches = re.findall(markup_regex, text)
    if len(matches) > 0:
        link_text = text[:text.index('[')]
        if link_text != '':
            linkPara.items.append(Text(link_text))
        linkPara.items.append(Link(matches[0][0], matches[0][1]))
        linkPara.items.append(parseLink(text[text.index(')') + 1:]))
    return linkPara if len(linkPara.items) > 0 else Text(text)


def findHeader(block):
    headerMatch = re.findall(r'^#{1,6}', block, flags=re.M)
    headerItems = re.split(r'^#{1,6}', block, flags=re.M)[1:]
    if len(headerMatch) > 0:
        return Paragraph(list(map( mapHeader,zip(headerMatch, headerItems))))
    return block

def mapHeader(match):
    return Header(len(match[0]), match[1].strip())

class Markdown(object):
    def __init__(self, blocks):
        self.blocks = blocks

    def __repr__(self):
        return 'Markdown({!r})'.format(self.blocks)


class Paragraph(object):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return 'Paragraph({!r})'.format(self.items)


class List(object):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return 'List({!r})'.format(self.items)


class Text(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Text({!r})'.format(self.text)


class Emphasis(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Emphasis({!r})'.format(self.text)


class Bold(object):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Bold({!r})'.format(self.text)


class Header(object):
    def __init__(self, level, items):
        self.level = level
        self.items = items

    def __repr__(self):
        return 'Header({},{!r})'.format(self.level, self.items)
    
class Link(object):
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def __repr__(self):
        return 'Link({!r})'.format(self.text)

class CodeBlock(object):
    def __init__(self, code, language="javascript"):
        self.code = code
        self.language = language

    def __repr__(self):
        return 'CodeBlock({!r})'.format(self.code)
    
class Image(object):
    def __init__(self, alt, url):
        self.alt = alt
        self.url = url

    def __repr__(self):
        return 'Image({!r})'.format(self.alt)


INLINE_ELEMENTS = [
    (r'\*\*([^\*]*)\*\*', Bold),
    (r'\*([^\*]*)\*', Emphasis),
]