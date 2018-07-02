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

import clr
clr.AddReference('System.Xml') 

from System.String import IsNullOrEmpty
from System.Xml import XmlReader, XmlNodeType, XmlReaderSettings, DtdProcessing
from System.IO import StringReader

class XmlNode(object):
   def __init__(self, xr):
      self.name = xr.LocalName
      self.namespace = xr.NamespaceURI
      self.prefix = xr.Prefix
      self.value = xr.Value
      self.nodeType = xr.NodeType

      if xr.NodeType == XmlNodeType.Element:
         self.attributes = []
         while xr.MoveToNextAttribute():
            if xr.NamespaceURI == 'http://www.w3.org/2000/xmlns/':
               continue
            self.attributes.append(XmlNode(xr))
         xr.MoveToElement()
      
   @property
   def xname(self):
      if IsNullOrEmpty(self.namespace):
         return self.name
      return "{%(namespace)s}%(name)s" % self.__dict__
    
  
def parse(xml):
   # see issue 379, and https://stackoverflow.com/questions/215854/
   settings = XmlReaderSettings();
   settings.XmlResolver = None;
   settings.DtdProcessing = DtdProcessing.Ignore;
   settings.ProhibitDtd = False;
   
   with XmlReader.Create(xml, settings) as xr:
      while xr.Read():
         xr.MoveToContent()
         node = XmlNode(xr)
         yield node
         if xr.IsEmptyElement:
            node.nodeType = XmlNodeType.EndElement
            del node.attributes
            yield node
  
def parseString(xml):
   return parse(StringReader(xml))

if __name__ == "__main__":
   nodes = parse('http://feeds.feedburner.com/Devhawk')   
   