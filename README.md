# HTML-Tag-Extractor-with-DIFF
Example of build Tag tree for full website (based on Springer test website) in file springerBuiltTree.txt

                    ┌meta
               ┌head┤
               │    ├script
               │    ├title
               │    ├meta
               │    └meta
           html┤
               │    ┌script
               │    ├script
               │    ├span
               │    ├noscript┐
               │    │        └iframe
               │    ├nav┐
               │    │   └a
               └body┤
                    │   ┌div

[...] (fragment above [main file is more than 1000 lines)

Working HTML Differencer in the main file, again based on test Springer websites.

Project Based on lxml, difflib

When we create the Website Object, we can access to each tag via it's name(class/id) or relative path.
Examples: 
Website1.getTagContent("//title").lstrip().splitlines()
Website1.getTagContent("//html/head/meta[@name='citation_author_institution']") #for 1.html

