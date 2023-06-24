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

        for item in lists.items:
            match = re.search(r'\s+[-|\*]\s+', item.items[0].text)
            if match is not None:
                inner_items = [inner_item.strip() for inner_item in re.split(r'\s+[-|\*]\s+', item.items[0].text, flags=re.M)]
                item.items = list()
                item.items.append(parse_paragraph(inner_items[0]))
                inner_lists = List(map(parse_paragraph, inner_items[1:]))
                item.items.append(inner_lists)
        return lists
    return parse_paragraph(block)

def parse_paragraph(block):
    parts = re.split('(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)', block)  # split out Emphasis and Bold
    return Paragraph(list(map(parse_inlines, parts)))

def parse_inlines(string):
    '''Parse Emphasis and Bold
    '''
    for regexp, klass in INLINE_ELEMENTS:
        match = re.match(regexp, string)
        if match is not None:
            return klass(match.group(1))
    return Text(string)
    
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


INLINE_ELEMENTS = [
    (r'\*\*([^\*]*)\*\*', Bold),
    (r'\*([^\*]*)\*', Emphasis)
]