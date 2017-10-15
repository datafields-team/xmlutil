# xmlutil
this package extrats data from xml tree with bfs algorithm and transforms it into a table with petl.<br />
it depends on packages ``xml.etree`` or ``lxml.etree`` and ``petl``.<br />
xml檔案解析輔助類。依賴``xml.etree`` 或 ``lxml.etree`` 以及``petl``。

# expands xml tree into a petl table
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

>>> country.expand2table(with_attrib=True, exclusive_tags=('rank', 'year',), with_element=True).lookall()
+-------------------------------------------+-----------------------------------------+--------------------------------------------+
| country                                   | gdppc                                   | neighbor                                   |
+===========================================+=========================================+============================================+
| <Element 'country' at 0x0000000003C6C060> | <Element 'gdppc' at 0x0000000003C6C0F0> | <Element 'neighbor' at 0x0000000003C6C180> |
+-------------------------------------------+-----------------------------------------+--------------------------------------------+
| <Element 'country' at 0x0000000003C6C060> | <Element 'gdppc' at 0x0000000003C6C0F0> | <Element 'neighbor' at 0x0000000003C6C1E0> |
+-------------------------------------------+-----------------------------------------+--------------------------------------------+

>>>
```
