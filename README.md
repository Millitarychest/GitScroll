

# GitScroll

A markdown and git based static site cms.

Take notes, write documentation or host a blog. GitScroll enables you to create fast and easy online presence.

### Features : 

* Password protect your blog with the help of [staticrypt](https://github.com/robinmoisson/staticrypt)
    (Do not store sensitive information)
* Code Syntax highlighting via [prism.js](https://prismjs.com/index.html)

### Usage:

```bash
 
python3 gitscroll.py
 
```

### Markdown function syntax

Set a pages password:

```Markdown
<-->password:<your_pass><-->
```

Set a pages position in its section:

```Markdown
<-->pos:<index><-->
```
or
```markdown
<-->pos:<index><-->
```


### Dependencies:

* [python3](https://www.python.org/)
* [staticrypt](https://github.com/robinmoisson/staticrypt)


### Roadmap

- ? extract standard html components to one location (eg. components.conf or smth)
- Webeditor (image pasting / uploading , Permissions / easy position setting) https://stackoverflow.com/a/64190649

### Issues

