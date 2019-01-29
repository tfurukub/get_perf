# -*- coding: UTF-8 -*-

# モジュールのインポート
import xml.etree.ElementTree as ET

# xmlファイルの読み込み
tree = ET.parse('test.xml')
ET.register_namespace('', 'urn:schemas-microsoft-com:unattend')
elem = tree.getroot()
for e in elem.findall("//Path",namespaces = {"urn:schemas-microsoft-com:unattend"}):
    print "aaa"
