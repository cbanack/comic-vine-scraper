#####################################################################################
#
#  Copyright (c) Harry Pierson. All rights reserved.
#
# This source code is subject to terms and conditions of the Microsoft Public License. 
# A  copy of the license can be found at http://opensource.org/licenses/ms-pl.html
# By using this source code in any fashion, you are agreeing to be bound 
# by the terms of the Microsoft Public License.
#
# You must not remove this notice, or any other, from this software.
#
#####################################################################################

import ipypulldom
from System.Xml import XmlNodeType
  
class _type_factory(object):
   class _type_node(object):
      def __init__(self, node):
         ty = type(node)
         self.name = ty.__name__
         self.namespace = ty.xmlns
    
   def __init__(self):
      self.types = {}

   def find_type(self, node, parent):
      def create_type(node, parent): 
         return type(node.name, (parent,), {'xmlns':node.namespace})

      if parent not in self.types:
         self.types[parent] = {}
    
      tp = self.types[parent]
      if node.name not in tp:
         tp[node.name] = [create_type(node, parent)]
    
      tpn = tp[node.name]
    
      for t in tpn:
         if t.xmlns == node.namespace: 
            return t
    
      #if there's no matching namespace type, create one and add it to the list
      new_type = create_type(node, parent)
      tpn.append(new_type)
      return new_type
  
   def __call__(self, node, parent=object):
      if isinstance(node, ipypulldom.XmlNode):
         return self.find_type(node, parent) 
      return self.find_type(self._type_node(node), parent)


xtype = _type_factory()

  
def xml2py(nodelist):
  
   def children(nodelist):
      while True:
         child = xml2py(nodelist)
         if child is None:
            break
         yield child
  
   def set_attribute(parent, child):
      name = type(child).__name__
      if not hasattr(parent, name):
         setattr(parent, name, child)
      else:
         val = getattr(parent, name)
         if isinstance(val, list):
            val.append(child)
         else:
            setattr(parent, name, [val, child])
      
   node = nodelist.next()
   if node.nodeType == XmlNodeType.EndElement:
      return None
    
   elif node.nodeType == XmlNodeType.Text or node.nodeType == XmlNodeType.CDATA:
      return node.value
    
   elif node.nodeType == XmlNodeType.Element:

      #create a new object type named for the element name
      cur = xtype(node)()
      cur._nodetype = XmlNodeType.Element
  
      #collect all the attributes and children in lists
      attributes = [xtype(attr, str)(attr.value) for attr in node.attributes]
      children = [child for child in children(nodelist)]
    
      if len(children) == 1 and isinstance(children[0], str):
         #fold up elements with a single text node
         cur = xtype(cur, str)(children[0])
         cur._nodetype = XmlNodeType.Element
      else:
         #otherwise, add child elements as properties on the current node
         for child in children:
            set_attribute(cur, child)

      for attr in attributes:
         attr._nodetype = XmlNodeType.Attribute
         set_attribute(cur, attr)
             
      return cur


def parse(xml):
   return xml2py(ipypulldom.parse(xml))
  
def parseString(xml):
   return xml2py(ipypulldom.parseString(xml))
  

if __name__ == '__main__':  
   rss = parse('http://feeds.feedburner.com/Devhawk')
   for item in rss.channel.item:
      print item.title
