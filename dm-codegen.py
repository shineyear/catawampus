#!/usr/bin/python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""Code Generator for XML access classes for CWMP DeviceModel objects.

Generates classes to parse and emit XML for objects defined using tr-106
device models.

DeviceModel files expected to be passed to be passed to this code generator
include:
http://www.broadband-forum.org/cwmp/tr-098-1-0-0.xml
http://www.broadband-forum.org/cwmp/tr-098-1-1-0.xml
http://www.broadband-forum.org/cwmp/tr-098-1-2-0.xml
http://www.broadband-forum.org/cwmp/tr-181-2-0-1.xml
http://www.broadband-forum.org/cwmp/tr-181-2-1-0.xml
http://www.broadband-forum.org/cwmp/tr-181-2-2-0.xml

This code generator itself relies on code generated for cwmp-datamodel-1-3.xsd
by generateDS. Its code generation all the way down.
"""

__author__ = 'dgentry@google.com (Denton Gentry)'

import cwmp_datamodel_1_3 as dm
import optparse
import string
import sys
import xml.etree.ElementTree as etree

def EmitPrologue():
  print("#!/usr/bin/python")
  print("#\n# THIS FILE IS GENERATED BY " + sys.argv[0])
  print("# DO NOT MAKE CHANGES HERE, THEY WILL BE OVERWRITTEN.\n")
  print("\"\"\"Classes to parse and emit XML for DeviceModel objects "
        "defined in CWMP specs.\n\"\"\"\n")

def XmlNameMangle(XMLname):
  """Convert an XML object name to a suitable Python class name.

  Examples:
    Device.Routing.RIP. returns Device_Routing_RIP_
    Device.Ethernet.Link.{i}.Stats. returns Device_Ethernet_Link_0i0_Stats_

  Args:
    XMLname - the object name taken directly from the XML file.

  Returns:
    A suitable Python class name.
  """
  tab = string.maketrans(".{}", "_00")
  return string.translate(XMLname, tab)


def EmitParameter(param, prefix=""):
  defvalue = "None"
  if hasattr(param.syntax.default, "value"):
    if param.syntax.boolean:
      defvalue = (param.syntax.default.value == "true")
    elif param.syntax.string:
      defvalue = '"' + param.syntax.default.value + '"'
    else:
      defvalue = param.syntax.default.value
  print "{0}p_{1} = {2}".format(prefix, param.name, defvalue)

def EmitClassForObj(obj):
  """Generate a class for a CWMP DeviceModel <object>.

  Args:
    obj - a generateDS object for a DeviceModel <object> node.
  """
  print "class {0}:".format(XmlNameMangle(obj.name))
  print "  def __init__(self):"
  print "    pass"
  print ""

  if len(obj.parameter) > 0:
    print "  # <parameter> variables"
    for param in obj.parameter:
      EmitParameter(param, "  ")
    print ""


def WhatToEmit(objects, emit_these):
  """Intersect objects with emit_these. If emit_these is empty, return all.

  Args:
    objects - list of object names
    emit_these - frozenset of object names to emit

  Returns:
    list of object names to emit
  """
  if emit_these:
    return [obj for obj in objects if obj in emit_these]
  else:
    return objects


def ParseDeviceModelFile(filename, emit_these):
  """Parse an XML file, emitting Python classes for DeviceModel objects.

  The device model is defined in tr-106, which provides an XML schema to
  validate DeviceModel definition files.
  http://www.broadband-forum.org/cwmp/tr-106-1-2-0.xml
  The current schema (at the time of this writing) is:
  http://www.broadband-forum.org/cwmp/cwmp-datamodel-1-3.xsd

  The general XML format is:
  <document>
    <component>
      <object> - objects which can go at several top level models
    <model>
      <object> - objects specific to a model

  Args:
    emit_these - a frozenset of object names for which classes should be
      generated.  If None, _all_ objects will be generated.
  """
  root = dm.parse(filename)
  for model in root.model:
    for obj in WhatToEmit(model.object, emit_these):
      EmitClassForObj(obj)


def ParseCmdline():
  """Handle command line arguments.
  """
  optparser = optparse.OptionParser(
      description='Code generator for tr181 objects')
  optparser.add_option('--outfile', help="filename to write generated code to.")
  return optparser.parse_args()


def main():
  (options, args) = ParseCmdline()
  if options.outfile:
    sys.stdout = open(options.outfile, "w")
  tr181_objects = frozenset(args)
  EmitPrologue()
  ParseDeviceModelFile('schema/tr-181-2-0-1.xml', tr181_objects)

if __name__ == '__main__':
  main()