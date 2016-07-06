from __future__ import unicode_literals
import xml.etree.ElementTree as etree
import os
import base64

class OTRSObject(object):
    """ Represents an object for OTRS (mappable to an XML element)
    """

    # Map : {'TagName' -> Class}

    CHILD_MAP = {}

    def __init__(self, *args, **kwargs):
        self.attrs = kwargs
        self.childs = {}

    def __getattr__(self, k):
        """ attrs are simple xml child tags (<tag>val</tag>), complex children,
        are accessible via dedicated methods.

        @returns a simple type
        """
        return autocast(self.attrs[k])

    @classmethod
    def from_xml(cls, xml_element):
        """
        @param xml_element an etree.Element
        @returns an OTRSObject
        """
        child_tags = cls.CHILD_MAP.keys()

        if not xml_element.tag.endswith(cls.XML_NAME):
            raise ValueError(
                'xml_element should be a {} node, not {}'.format(
                    cls.XML_NAME, xml_element.tag))
        attrs = {}
        childs = []
        for t in xml_element.getchildren():
            name = extract_tagname(t)
            if name in child_tags:
                # Complex child tags
                SubClass = cls.CHILD_MAP[name]
                sub_obj = SubClass.from_xml(t)
                childs.append(sub_obj)
            else:
                # Simple child tags
                attrs[name] = t.text
        obj = cls(**attrs)

        for i in childs:
            obj.add_child(i)

        return obj

    def add_child(self, childobj):
        """
        @param childobj : an OTRSObject
        """
        xml_name = childobj.XML_NAME

        if xml_name in self.childs:
            self.childs[xml_name].append(childobj)
        else:
            self.childs[xml_name] = [childobj]

    def check_fields(self, fields):
        """ Checks that the list of fields is bound
        @param fields rules, as list

        items n fields can be either :
         - a field name : this field is required
         - a tuple of field names : on of this fields is required
        """
        set_keys = set(self.attrs.keys())

        for i in fields:
            if isinstance(i, str):
                set_fields = set([i])
            else:
                set_fields = set(i)

            if set_keys.intersection(set_fields):
                valid = True
            else:
                valid = False

            if not valid:
                raise ValueError('{} should be filled'.format(i))

    def to_xml(self):
        """
        @returns am etree.Element
        """
        root = etree.Element(self.XML_NAME)
        for k, v in self.attrs.items():
            e = etree.Element(k)
            if isinstance(e, str):  #  True
                v = v.encode('utf-8')
            e.text = unicode(v)
            root.append(e)
        return root

def extract_tagname(element):
    """ Returns the name of the tag, without namespace

    element.tag lib gives "{namespace}tagname", we want only "tagname"

    @param element : an etree.Element
    @returns       : a str, the name of the tag
    """
    qualified_name = element.tag
    try:
        return qualified_name.split('}')[1]
    except IndexError:
        # if it's not namespaced, then return the tag name itself
        return element.tag
        #raise ValueError('"{}" is not a tag name'.format(qualified_name))


def autocast(s):
    """ Tries to guess the simple type and convert the value to it.

    @param s string
    @returns the relevant type : a float, string or int
    """

    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

# the four functions below are here only for backward compatibility
# with old code that imported these classes from this file
# the classes are now in tickets/objects.py

def Ticket(*args, **kwargs):
    import ticket.objects
    return ticket.objects.Ticket(*args, **kwargs)

def Article(*args, **kwargs):
    import ticket.objects
    return ticket.objects.Article(*args, **kwargs)

def DynamicField(*args, **kwargs):
    import ticket.objects
    return ticket.objects.DynamicField(*args, **kwargs)

def Attachment(*args, **kwargs):
    import ticket.objects
    return ticket.objects.Attachment(*args, **kwargs)
