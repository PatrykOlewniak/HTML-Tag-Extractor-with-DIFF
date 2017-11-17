# -*- coding: utf-8 -*-

import difflib
from lxml import html
from urllib2 import urlopen

#########################################################################################
##### Tag Classes
#########################################################################################


class Tag:
    def __init__(self, tagName, attribute, content=None, head=None, fullDescription=False):
        self.tagName = tagName
        self.attribute = attribute
        self.content = content
        self.subElements = []
        if fullDescription:
            self.tagName = self.tagName+str(attribute)
        if head:
            head.subElements.append(self)

    def __str__(self):
        return self.tagName


#########################################################################################
##### Website Main class
#########################################################################################

class Website(object):
    def __init__(self, path, websiteContents=None, root=None, treeHtmlHead=None, tree=None,fullTagDescription=False):
        self.path = path
        self.websiteContents = websiteContents
        self.root = root
        self.tree = tree
        self.fullTagDescription = fullTagDescription #in future to implement turn off/on switch
        self.treeHtmlHead = treeHtmlHead
        self._setSiteContents()
        self._setRootOfWebsite()
        self._setTreeOfWebsite()
        self.tagList = []
        self._setSiteTagsList()
        self._prepareTree()

    def __repr__(self):
        return str(self.getSiteContents())

    def _setSiteContents(self):
        """Initial method for retrieving website (from url or file)"""
        if "http" in self.path:
            response = urlopen(self.path)
            self.websiteContents = response.read()
        else:
            try:
                self.websiteContents = open(self.path, "r").read()
            except Exception:
                print ("Sorry, cant open the file")


    def getSiteContents(self):
        return self.websiteContents

    def _setRootOfWebsite(self):
        self.root = html.fromstring(self.websiteContents)

    def _setTreeOfWebsite(self):
        self.tree = self.root

    def _setSiteTagsList(self):
            tags = self.tree.cssselect("*")
            for tag in tags:
                self.tagList.append((tag.tag, dict(tag.attrib)))

    def getSiteTagsList(self):
        return self.tagList

    def getChildTagsList(self, XPATH, onlyFirstOneMatching=True):
        """
        :param onlyFirstOneMatching: True by default, if false: returns list of all matching tag elements
        :return: list of elements with children of tag
        """
        childtagList = []
        tagElement = self.tree.xpath(XPATH)
        if onlyFirstOneMatching:
            tagElement = tagElement[0].iterchildren()
            for element in tagElement:
                childtagList.append((element.tag, dict(element.attrib)))
        else:
            for elem in tagElement:
                elemIter = elem.iterchildren()
                for subelement in elemIter:
                    childtagList.append((subelement.tag, dict(subelement.attrib)))
        return childtagList


    def getTagContent(self, XPath, onlyFirst=True, text_content=False):
        """if onlyFirst=True(default on): get first element with selected if. If False: tuple list (tag,text,attrib)
        There is little problem with metadata. Metas don't have text value, only attrib"""
        #TODO: implement text_content for html inside """desc: Returns the text content of the element, including the text content of its children, with no markup."""

        if "meta" in XPath:
            return self._getMetaTagContent(XPath)
        selectedTagContent = self.tree.xpath(XPath)
        if onlyFirst is True and len(selectedTagContent) and isinstance(selectedTagContent,list):
            return selectedTagContent[0].text
        if onlyFirst is False and len(selectedTagContent) and isinstance(selectedTagContent,list):
            tempTagTextList=[]
            for element in selectedTagContent:
                tempTagTextList.append((element.tag, element.text, element.attrib))
            return tempTagTextList
        else:
            return selectedTagContent

    def _getMetaTagContent(self, XPath, onlyFirst=True):
        """Method for metadata. Metadata doesn't have text content (only atribb/values)
            Returns attribute list with tuple [(key,value),...]
            For example with right site : //html/head/meta[@name='citation_author_institution'] returns
            [('name', 'citation_author_institution'), ('content', 'Univesitet Paris')]"""
        selectedTagContent = self.tree.xpath(XPath)
        if len(selectedTagContent) and isinstance(selectedTagContent,list):
            metaDataElem =  selectedTagContent[0].attrib
            try:
                tempMetaTagList=[]
                k = metaDataElem.iterkeys()
                for i in k:
                    tempMetaTagList.append((i,metaDataElem[i]))
                return tempMetaTagList
            except:
                return selectedTagContent[0].attrib
        else:
            return None

    def getTagOccurencesNumber(self, XPath):
        """returns number of found elements in website - using Xpath"""
        return int(self.tree.xpath("count("+str(XPath)+")"))


    def printTree(self, filePath=None):
        """
        If we choose to file (with filepath) we reload sys module for change the stdout dest.
        :param filePath: If file path: printing output to file with selected path
        """
        if filePath:
            import sys
            sys.stdout = open(filePath, "w")
            self._treePrinter(self.treeHtmlHead)
            sys.stdout = sys.__stdout__
        else:
            self._treePrinter(self.treeHtmlHead)

    def _prepareTree(self):
        HTML = Tag(self.tree.tag, self.tree.attrib, self.tree.text, head=None)
        self.treeHtmlHead = HTML
        tempHead = HTML
        for children in self.tree.iterchildren():
            name = Tag(children.tag, children.attrib, children.text, head=tempHead)
            def subChildrens(childX, name):
                for child in childX.iterchildren():
                    name1 = Tag(child.tag, child.attrib, child.text, head=name)

                    subChildrens(child,name1)
            subChildrens(children, name)

    def _treePrinter(self, current_node="self.treeHtmlHead",
                     childattr='subElements',
                     nameattr='tagName',
                     indent='',
                     last='updown'):
        if hasattr(current_node, nameattr):
            name = lambda node: getattr(node, nameattr)
        else:
            name = lambda node: str(node)

        children = lambda node: getattr(node, childattr)
        nb_children = lambda node: sum(nb_children(child) for child in children(node)) + 1
        size_branch = {child: nb_children(child) for child in children(current_node)}

        """ Creation of balanced lists for "up" branch and "down" branch. """
        up = sorted(children(current_node), key=lambda node: nb_children(node))
        down = []
        while up and sum(size_branch[node] for node in down) < sum(size_branch[node] for node in up):
            down.append(up.pop())

        """ Printing of "up" branch. """
        for child in up:
            next_last = 'up' if up.index(child) is 0 else ''
            next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in last else '│',
                                             ' ' * len(name(current_node)))
            self._treePrinter(child, childattr, nameattr, next_indent, next_last)

        """ Printing of current node. """
        if last == 'up':
            start_shape = '┌'
        elif last == 'down':
            start_shape = '└'
        elif last == 'updown':
            start_shape = ' '
        else:
            start_shape = '├'

        if up:
            end_shape = '┤'
        elif down:
            end_shape = '┐'
        else:
            end_shape = ''

        i = ('%s%s%s%s' % (indent, start_shape, name(current_node), end_shape))
        print i

        """ Printing of "down" branch. """
        for child in down:
            next_last = 'down' if down.index(child) is len(down) - 1 else ''
            next_indent = '%s%s%s' % (indent,
                                      ' ' if 'down' in last else '│',
                                      ' ' * len(name(current_node)))
            self._treePrinter(child, childattr, nameattr, next_indent, next_last)


if __name__ == "__main__":
    website1 = Website("test/websites/springer1.html")
    website2 = Website("test/websites/springer2.html")
    wwebsite1 = website1.getSiteContents().strip().splitlines()
    wwebsite2 = website2.getSiteContents().strip().splitlines()
    wwebsite1 = [x.lstrip() for x in wwebsite1]
    wwebsite2 = [x.lstrip() for x in wwebsite2]

    diff = difflib.HtmlDiff(tabsize=8, wrapcolumn=60).make_file(wwebsite1, wwebsite2)
    file = (open('testThirdDiff.html', "w"))
    file.write(diff)
    file.close()

    website1 = Website("test/websites/springer1.html")
    website1.printTree("springerBuiltTree.py")