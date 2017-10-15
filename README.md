# xmlutil
基於Python 套件 lxml/petl 的 xml 解析工具

# dfs expands xml tree into a petl table
```
>>> from xml.etree import cElementTree as ET
>>> text = """<?xml version="1.0"?>
...         <data>
...             <country name="Liechtenstein">
...                 <rank>1</rank>
...                 <year>2008</year>
...                 <gdppc>141100</gdppc>
...                 <neighbor name="Austria" direction="E"/>
...                 <neighbor name="Switzerland" direction="W"/>
...             </country>
...             <country name="Singapore">
...                 <rank>4</rank>
...                 <year>2011</year>
...                 <gdppc>59900</gdppc>
...                 <neighbor name="Malaysia" direction="N"/>
...             </country>
...         </data>
... """
>>> element = ET.fromstring(text)
>>>
>>> import xmlutil
>>> node = xmlutil.XMLNode(element)
>>> country = node.find('.//country')
>>> countries = node.findall('.//country')
>>>
>>> table = country.expand2table() # expands country into a petl table
>>> table.lookall()                # views table
+------+--------+----------+
| rank | year   | gdppc    |
+======+========+==========+
| '1'  | '2008' | '141100' |
+------+--------+----------+

>>> for dic in table.dicts():
...     print dic
...
{u'gdppc': '141100', u'rank': '1', u'year': '2008'}
>>> country.expand2table(with_attrib=True).lookall()
+---------------------------+------+--------+----------+-------------------------------------------+
| country                   | rank | year   | gdppc    | neighbor                                  |
+===========================+======+========+==========+===========================================+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+------+--------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+------+--------+----------+-------------------------------------------+

>>> country.expand2table(with_attrib=True, exclusive_tags=('rank', 'year',)).lookall()
+---------------------------+----------+-------------------------------------------+
| country                   | gdppc    | neighbor                                  |
+===========================+==========+===========================================+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+----------+-------------------------------------------+

>>> country.expand2table(with_attrib=True, exclusive_tags=('rank', 'year',), duplicate_tags=('neighbor',)).lookall()
+---------------------------+----------+---------------------------------------+-------------------------------------------+
| country                   | gdppc    | neighbor                              | neighbor_1                                |
+===========================+==========+=======================================+===========================================+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'E', 'name': 'Austria'} | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+----------+---------------------------------------+-------------------------------------------+

>>>
```
