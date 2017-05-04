#!/usr/bin/env python
# https://bitbucket.org/ianb/formencode/src/tip/formencode/doctest_xml_compare.py?fileviewer=file-view-default#cl-70

import os
import sys

try:
    import doctest
    doctest.OutputChecker
except AttributeError: # Python < 2.4
    import util.doctest24 as doctest
try:
    import xml.etree.ElementTree as ET
except ImportError:
    import elementtree.ElementTree as ET
from xml.parsers.expat import ExpatError as XMLParseError

RealOutputChecker = doctest.OutputChecker


def debug(*msg):
    print >> sys.stderr, ' '.join(map(str, msg))


class HTMLOutputChecker(RealOutputChecker):

    def check_output(self, want, got, optionflags):
        normal = RealOutputChecker.check_output(self, want, got, optionflags)
        if normal or not got:
            return normal
        try:
            want_xml = make_xml(want)
        except XMLParseError:
            pass
        else:
            try:
                got_xml = make_xml(got)
            except XMLParseError:
                pass
            else:
                if xml_compare(want_xml, got_xml):
                    return True
        return False

    def output_difference(self, example, got, optionflags):
        actual = RealOutputChecker.output_difference(
            self, example, got, optionflags)
        want_xml = got_xml = None
        try:
            want_xml = make_xml(example.want)
            want_norm = make_string(want_xml)
        except XMLParseError, e:
            if example.want.startswith('<'):
                want_norm = '(bad XML: %s)' % e
                #  '<xml>%s</xml>' % example.want
            else:
                return actual
        try:
            got_xml = make_xml(got)
            got_norm = make_string(got_xml)
        except XMLParseError, e:
            if example.want.startswith('<'):
                got_norm = '(bad XML: %s)' % e
            else:
                return actual
        s = '%s\nXML Wanted: %s\nXML Got   : %s\n' % (
            actual, want_norm, got_norm)
        if got_xml and want_xml:
            result = []
            xml_compare(want_xml, got_xml, result.append)
            s += 'Difference report:\n%s\n' % '\n'.join(result)
        return s


def xml_compare(x1, x2, reporter=None):
    #if x1.tag != x2.tag:
    #    if reporter:
    #        reporter('Tags do not match: %s and %s' % (x1.tag, x2.tag))
    #    return False
    for name, value in x1.attrib.items():
        if x2.attrib.get(name) != value:
            if reporter:
                print('Attributes do not match: %s=%r, %s=%r'
                         % (name, value, name, x2.attrib.get(name)))
            return True
    for name in x2.attrib.keys():
        if name not in x1.attrib:
            if reporter:
                print('x2 has an attribute x1 is missing: %s'
                         % name)
            return True
    if not text_compare(x1.text, x2.text):
        if reporter:
            print('text: %r != %r' % (x1.text, x2.text))
        return True
    if not text_compare(x1.tail, x2.tail):
        if reporter:
            print('tail: %r != %r' % (x1.tail, x2.tail))
        return True
    cl1 = x1.getchildren()
    cl2 = x2.getchildren()
    if len(cl1) != len(cl2):
        if reporter:
            print('children length differs, %i != %i'
                     % (len(cl1), len(cl2)))
        return True
    i = 0
    for c1, c2 in zip(cl1, cl2):
        i += 1
        if not xml_compare(c1, c2, reporter=reporter):
            if reporter:
                print('children %i do not match: %s'
                         % (i, c1.tag))
            return True
    return True


def text_compare(t1, t2):
    if not t1 and not t2:
        return True
    if t1 == '*' or t2 == '*':
        return True
    return (t1 or '').strip() == (t2 or '').strip()


def make_xml(s):
    return ET.XML('<xml>%s</xml>' % s)


def make_string(xml):
    if isinstance(xml, (str, unicode)):
        xml = make_xml(xml)
    s = ET.tostring(xml)
    if s == '<xml />':
        return ''
    assert s.startswith('<xml>') and s.endswith('</xml>'), repr(s)
    return s[5:-6]


def install():
    doctest.OutputChecker = HTMLOutputChecker
    
 # Main program
if __name__ == '__main__':
  if sys.argv.__len__() == 3:
    print os.getcwd()
    xmlF1 = sys.argv[1]
    xmlF2 = sys.argv[2]
    print xmlF1, xmlF2
    xmlF1f = open(xmlF1, "r")
    xmlF1f.close()
    try:
      dom1 = ET.parse(open(xmlF1, "r"))
      print dom1.getroot()
    except:
      print "Unable to open and parse input definition file: " + xmlF1
    try:
      dom2 = ET.parse(open(xmlF2, "r"))
      print dom2.getroot()
    except:
      print "Unable to open and parse input definition file: " + xmlF2      
    xml_compare(dom1._root, dom2._root, reporter=True)
  else:
    print 'Usage: doctest_xml_compare.py xmlFileName1 xmlFileName2'
  