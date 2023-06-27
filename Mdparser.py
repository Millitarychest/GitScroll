import re


def parseMD(rawMD):
    #getBlocks
    #print( Markdown([parseBlock(block) for block in split_into_blocks(rawMD)]) )
    return Markdown([parseBlock(block) for block in split_into_blocks(rawMD)])

def contains_only_newlines(string):
    return re.match(r'^\n*$', string) is not None

def split_into_blocks(string):
    blocks =  re.split(r'\n{2,}', string)

    codeblocks = re.findall(r'(```(\w+)\n([\n\s\S]*?)\n*```)', string, flags=re.M)



    final_blocks = []
    current_block = ''
    codeBlockcounter = 0
    was_code = 0
    for index, block in enumerate(blocks):
        if was_code == 0:
            if block.startswith('```') and not block.endswith('```'):
                #current_block = block
                current_block = codeblocks[codeBlockcounter][0]
                codeBlockcounter += 1
                while not blocks[index].endswith('```'):
                    #current_block += "\n"
                    index += 1
                    #current_block += blocks[index]
                    was_code += 1
                final_blocks.append(current_block)
   
            else: 
                if not contains_only_newlines(block):
                    final_blocks.append(block)
        else:
            was_code -= 1
    
    return final_blocks

def parse_block_quotes(lines):
    
    quotes = []
    current_quote = ''
    was_quote = False
    for line in lines:
        if re.sub(r"^(\s*\t*>+[\s*>*]*)", "", line) is not "":
            quotes.append(BlockQuote(re.sub(r"^(\s*\t*>+[\s*>*]*)", "", line) + "\n", count_block_quotes(line)))
    quotes.append(BlockQuote("", -1))
    
    return BlockQuotes(quotes)

def count_block_quotes(line):
    match = re.findall(r'^(\s*\t*>+[\s*>*]*)', line)
    if match:
        
        matches = [matche.replace(" ", "") for matche in match]
        return len(matches[0])- 1
    else:
        return 0

def parseBlock(block):
    #get headers
    block = findHeader(block)
    if not isinstance(block, str):
        for header in block.items:
            parts = re.split('(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)', header.items)
            header.items = list(map(parse_inlines, parts))
        return block
    
    #get horizontal rules
    match = re.match(r'(^-{3,})', block)
    if match is not None:
        return HorRule()
    
    #get block quotes
    if block.startswith('>'):
        lines = re.split(r'\n', block)
        quotes = parse_block_quotes(lines)
        return quotes
    
    #get lists
        
    match = re.match(r'^\s*[-*+]\s+', block)
    if match is not None:
        lines = re.split(r'\n', block)
        indents = [len(re.match(r'^\s*', line).group()) for line in lines]
    
        
        if any(indent > 0 for indent in indents):
            return parse_list_items(lines, indents)

        
        lists = parse_list_items(lines, [0])
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
    inlines_regex = '(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*|!\\[[^\\]]+\\]\\([^\\)]+\\)|\\[[^\\]]+\\]\\([^\\)]+\\)|`[^`]+`)'
    #inlines_regex = '(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*|!\\[[^\\]]+\\]\\([^\\)]+\\))'
    #inlines_regex = '(\\*\\*[^\\*]*\\*\\*|\\*[^\\*]*\\*)'
    parts = re.split(inlines_regex, block)  # split out Emphasis and Bold
    return Paragraph(list(map(parse_inlines, parts)))

def parse_inlines(string):
    '''Parse Emphasis and Bold
    '''
    #print(string)
    if string is not None:
        for regexp, klass in INLINE_ELEMENTS:
            match = re.match(regexp, string)
            if match is not None:
                if klass == Link:
                    return klass(match.group(1), match.group(2))
                elif klass == CodeBlock:
                    return klass(match.group(1), fullCode=False)
                else:
                    return klass(match.group(1))
        match = re.match(r'!\[([^\]]+)\]\(([^)]+)\)', string)
        if match is not None:
            alt_text = match.group(1)
            image_url = match.group(2)
            return Image(alt_text, image_url)
    return Text(string)
    #return parseLink(string)



def parse_list_items(items, indents):
    while len(items) > len(indents):
        indents.append(0)

    lists = []
    for item, indent in zip(items, indents):
        if indent == 0:
            match = re.match(r'^\s*[-*+]\s+', item)
            if match is not None:
                lists.append(List([parse_paragraph(item.replace("*", "").replace("-", "").replace("+", "").strip())], 0))
            else:
                if len(lists) > 0:
                    lists[len(lists) - 1].items[len(lists[len(lists) - 1].items) - 1].items.append(Text(item.replace("*", "").strip() + "\n"))
                else:
                    lists.append(List([parse_paragraph(item.replace("*", "").strip())]))
        else:
            match = re.match(r'^\s*[-*+]\s+', item)
            if match is not None:
                if len(lists) > 0:
                    lists[len(lists) - 1].items.append(List([parse_paragraph(item.replace("*", "").strip())], indent / 4))
                else:
                    lists.append(List([List([parse_paragraph(item.replace("*", "").strip())])], indent / 4))
            else:
                if len(lists) > 0:
                    indenters = "\t" * int(indent / 4)
                    lists[len(lists) - 1].items[len(lists[len(lists) - 1].items) - 1].items.append(Text(indenters + item.replace("*", "").strip() + "\n"))
                else:
                    indenters = "\t" * int(indent / 4)
                    lists.append(List([parse_paragraph(indenters + item.replace("*", "").strip())]))

    return Paragraph(lists)




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
    def __init__(self, items, level=0):
        self.items = items
        self.level = level

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

class HorRule(object):
    def __init__(self):
        self.text = ""

    def __repr__(self):
        return 'Horizontal Rule({!r})'.format(self.text)

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
    def __init__(self, code, language="javascript", fullCode=True):
        self.code = code
        self.language = language
        self.fullCode = fullCode

    def __repr__(self):
        return 'CodeBlock({!r})'.format(self.code)
    
class Image(object):
    def __init__(self, alt, url):
        self.alt = alt
        self.url = url

    def __repr__(self):
        return 'Image({!r})'.format(self.alt)

class BlockQuote(object):
    def __init__(self, text, level=0):
        self.level = level
        self.text = text

    def __repr__(self):
        return 'BlockQuote({},{!r})'.format(self.level,self.text)

class BlockQuotes(object):
    def __init__(self, quotes):
        self.items = quotes

    def __repr__(self):
        return 'BlockQuotes({!r})'.format(self.items)

INLINE_ELEMENTS = [
    (r'\*\*([^\*]*)\*\*', Bold),
    (r'\*([^\*]*)\*', Emphasis),
    (r'\[([^\]]+)\]\(([^)]+)\)', Link),
    (r'`([^`]+)`', CodeBlock)
]