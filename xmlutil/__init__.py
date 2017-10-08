# -*- coding: utf-8 -*-
"""
Created on 2017年10月1日

@author: albin
"""
import re
import abc
import collections

from lxml import etree 
import petl

import sys
sys.path.insert(0, r'C:\Users\albin\Downloads\dbutil-20171007T105314Z-001\dbutil')


namespace_pattern = re.compile(r"{.+}")


def parse(filename, *args, **kwargs):
    element = etree.parse(filename, *args, **kwargs).getroot()
    return XMLNode(element)
    

def get_tag(element):
    return re.sub(namespace_pattern, '', element.tag)


class Node(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, element):
        """
        :param element: a instance of `lxml.etree.Element`"""
        if element is Node:
            raise TypeError('received None')
        self.element = element
    
    @abc.abstractmethod
    def expand2dicts(self, text_flag=True):
        """ expand the wrapped element. return: list<dict>"""

    def expand2table(self, text_flag=True):
        """ expand the wrapped element to a `petl.util.base.Table`
        :param text_flag:  the table contains of element's text if True otherwise contains of element.
        :return: <? extends `petl.util.base.Table`> table<?>"""
        dicts = self.expand2dicts(text_flag)
        return dicts2table(dicts)

    def findall(self, expression, **kwargs):
        """Wraps the result of executing expression into a `NodeList` and return it"""
        return self._execute_expression(self.element, 'findall', expression, **kwargs)
    
    def xpath(self, expression, **kwargs):
        """Wraps the result of executing expression into a `NodeList` and return it"""
        return self._execute_expression(self.element, 'xpath', expression, **kwargs)
        
    def _execute_expression(self, target_node, func_name, expression, **kwargs):
        """executing expression over target_node methods named func_name"""
        func = getattr(target_node, func_name)
        elements = func(expression, **kwargs)
        return NodeList(elements)
        
    def relate(this, other, relation='crossjoin', **petl_kwargs):
        """relate this node and other node as a `RelatedNode` over relation. relation is a method name of `petl.util.base.Table`"""
        return RelatedNode(this, other, relation, **petl_kwargs)
    
    def tag(self):
        return get_tag(self.element)

    def namespace(self):
        return re.sub(self.tag(), '', self.element.tag)

    def __repr__(self):
        return "<%s %s at 0x%x>" % (self.__class__.__name__, self.tag(), id(self))


class EmptyNode(Node):
    def __init__(self):
        pass
            
    def expand2dicts(self, text_flag=True):
        """implement"""
        return []

    def __repr__(self):
        return "<%s %s at 0x%x>" % (self.__class__.__name__, 'None', id(self))


class XMLNode(Node):
    def expand2dicts(self, text_flag=True):
        """implement"""
        dicts = DataBuilder(self.element, text_flag).build()
        return dicts
        
    def remove(self):
        parent = self.element.getparent()
        parent.remove(self.element)
        
    def find(self, expression, **kwargs):
        element = self.element.find(expression, **kwargs)
        return XMLNode(element)
       

        
class NodeList(Node, list):
    def __init__(self, elements):
        if not elements:
            raise TypeError('received empty list')
        nodes = element if isinstance(elements[0], Node) else [XMLNode(e) for e in elements]
        Node.__init__(self, nodes[0].element)
        self.extend(nodes)

    def expand2dicts(self, text_flag=True):
        """implement"""
        dicts = []
        for node in self:
            dicts.extend(node.expand2dicts(text_flag=True))
        return dicts

    def _execute_expression(self, target_node, func_name, expression, **kwargs):
        """overwrite"""
        nodes = []
        for node in self:
            nodes.extend(Node._execute_expression(node, func_name, expression, **kwargs))
        return NodeList(nodes)
        
    def remove(self):
        for node in self:
            node.remove()

    
class RelatedNode(Node):
    def __init__(self, this, other, relation, **kwargs):
        super(RelatedNode, self).__init__(this.element)
        self.this = this
        self.other = other
        self.relation = relation
        self.kwargs = kwargs

    def expand2dicts(self, text_flag=True):
        """implement"""
        return self.expand2table(text_flag).dicts()

    def expand2table(self, text_flag=True):
        """overwrite"""
        this_dicts = self.this.expand2dicts(text_flag)
        this_table = dicts2table(this_dicts)
        other_dicts = self.other.expand2dicts(text_flag)
        other_table = dicts2table(other_dicts)
        related_table = getattr(this_table, self.relation)(other_table, **self.kwargs)
        return related_table

    def _execute_expression(self, target_node, func_name, expression, **kwargs):
        """overwrite"""
        nodes1 = Node._execute_expression(self.this, func_name, expression, **kwargs)
        nodes2 = Node._execute_expression(self.other, func_name, expression, **kwargs)
        return NodeList(nodes1 + nodes2)
        

def dicts2table(dicts):
    """transform dicts into a `petl.util.base.Table`"""
    table = petl.wrap(petl.fromdicts(dicts))
    return table


class DataBuilder(object):
    """expand element tree to a `sequence` of `dict`
    :param element: lxml.etree.Element
    :param text_flag:  the table contains of element's text if True otherwise contains of element.
    """

    def __init__(self, element, text_flag=True):
        self.element = element
        self.text_flag = text_flag
        self.tmp_tags = list()
        self.data_list = list()
        self.data_item = collections.OrderedDict()

    def build(self):
        self._build(self.element)
        return self.data_list

    def _build(self, element, level=0):
        tag, text = get_tag(element), element.text.strip() if element.text else None
        if text:
            if self.data_item.get(tag) is not None:
                self._insert(tag)
            self.tmp_tags.append(tag)
            self.data_item.update({tag: text if self.text_flag else element})
        for e in element:
            self._build(e, level + 1)
        if level == 0:
            self._insert(tag)

    def _insert(self, duplicate_tag):
        self.data_list.append(self.data_item.copy())
        
        try:
            idx = self.tmp_tags.index(duplicate_tag)
        except: 
            idx = len(self.tmp_tags)
        for tag in self.tmp_tags[idx:]:
            self.data_item[tag] = None
        self.tmp_tags = self.tmp_tags[:idx]
