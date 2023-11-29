import io
import sys

from base import prepare_directory, traverse_directory
from collections import OrderedDict
from xml.etree.ElementTree import fromstring


def dump_ordered_dict(od, indent_level=0, indent='  '):
    ret = '{'
    for key, value in od.items():
        if key == '$$':
            continue
        ret += '"{}":"{}",'.format(
            key,
            value.replace('\\', '\\\\').replace('"', '\\"')
        )
    if not od.get('$$'):
        return ret[:-1] + '}' if ret[-1] == ',' else ret + '}'
    child_nodes = [dump_ordered_dict(c, indent_level+1) for c in od['$$']]
    ret += '"$$":[\n'
    for child in child_nodes[:-1]:
        ret += f'{indent * (indent_level + 1)}{child},\n'
    ret += f'{indent * (indent_level + 1)}{child_nodes[-1]}\n'
    return ret + '{}]{}'.format(indent*indent_level, '}')

def xml_to_ordered_dict(xml):
    ret = OrderedDict()
    child_nodes = [xml_to_ordered_dict(child) for child in xml]
    ret[f'${xml.tag}'] = xml.attrib['name']
    for key, value in xml.attrib.items():
        if key in ['name', 'basedata']:
            continue
        ret[key] = value
    if xml.attrib.get('basedata'):
        ret['basedata'] = xml.attrib.get('basedata')
    if child_nodes:
        ret['$$'] = child_nodes
    return ret

def xml_str_to_json_str(xml_str):
    xml = fromstring(xml_str)
    od = xml_to_ordered_dict(xml)
    return dump_ordered_dict(od)

def callback(in_filename, out_filename):
    f = io.open(in_filename, encoding='utf-8')
    xml_str = f.read().replace('&amp;lt;', '&lt;')
    f.close()

    res = xml_str_to_json_str(xml_str)

    prepare_directory(out_filename)

    f = io.open(out_filename.replace('.xml', '.json'), 'w', encoding='utf-8')
    f.write(res)
    f.close()

def main():
    traverse_directory(sys.argv[1], sys.argv[2], callback)

if __name__ == '__main__':
    main()
