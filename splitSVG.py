import xml.etree.ElementTree as ET
import copy
import os
import sys

def split_svg(filename):

    tree = ET.parse(sys.argv[1])
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
