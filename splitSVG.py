import xml.etree.ElementTree as ET
import copy
import os
import sys

# from https://stackoverflow.com/questions/54439309/how-to-preserve-namespaces-when-parsing-xml-via-elementtree-in-python
def register_all_namespaces(filename):
    namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
    for ns in namespaces:
        ET.register_namespace(ns, namespaces[ns])

def split_svg(filename):
    register_all_namespaces(filename)

    tree = ET.parse(filename)
    root = tree.getroot()
    layers = [g.get('{http://www.inkscape.org/namespaces/inkscape}label')
              for g in root.findall('{http://www.w3.org/2000/svg}g')]

    print(layers)

    for layer in layers:
        temp_tree = copy.deepcopy(tree)
        temp_root = temp_tree.getroot()
        for g in temp_root.findall('{http://www.w3.org/2000/svg}g'):
            name = g.get('{http://www.inkscape.org/namespaces/inkscape}label')
            if name in layers and name != layer:
                temp_root.remove(g)
        temp_tree.write(os.path.splitext(filename)[0] + '_' + layer + '.svg')

split_svg(sys.argv[1])
