# xmlutil
this package extrats data from xml tree with bfs algorithm and transforms data into a table with petl.<br />
it depends on packages ``xml.etree`` or ``lxml.etree`` and ``petl``.<br />

# expands xml tree into a petl table
```
>>> from lxml import etree
>>> text = """<?xml version="1.0"?>
...         <data>
...             <dataType>GDP</dataType>
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
>>> element = etree.fromstring(text)
>>> etree.ElementTree(element).write('country.xml') # dump to file
>>>
>>> import xmlutil
>>> node = xmlutil.parse('country.xml')  # node = xmlutil.XMLNode(element) is equivalent
>>> country = node.find('.//country')
>>> countries = node.findall('.//country')
>>>
>>> table = country.to_table() # expands country into a petl table
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
>>> country.to_table(with_attrib=True).lookall()
+---------------------------+------+--------+----------+-------------------------------------------+
| country                   | rank | year   | gdppc    | neighbor                                  |
+===========================+======+========+==========+===========================================+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+------+--------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+------+--------+----------+-------------------------------------------+

>>> country.to_table(with_attrib=True, exclusive_tags=('rank', 'year',)).lookall()
+---------------------------+----------+-------------------------------------------+
| country                   | gdppc    | neighbor                                  |
+===========================+==========+===========================================+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+----------+-------------------------------------------+

>>> country.to_table(with_attrib=True, exclusive_tags=('rank', 'year',), duplicate_tags=('neighbor',)).lookall()
+---------------------------+----------+---------------------------------------+-------------------------------------------+
| country                   | gdppc    | neighbor                              | neighbor_1                                |
+===========================+==========+=======================================+===========================================+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'E', 'name': 'Austria'} | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+----------+---------------------------------------+-------------------------------------------+

>>> country.to_table(with_attrib=True, exclusive_tags=('rank', 'year',), with_element=True).lookall()
+-------------------------------------------+-----------------------------------------+--------------------------------------------+
| country                                   | gdppc                                   | neighbor                                   |
+===========================================+=========================================+============================================+
| <Element 'country' at 0x0000000003C6C060> | <Element 'gdppc' at 0x0000000003C6C0F0> | <Element 'neighbor' at 0x0000000003C6C180> |
+-------------------------------------------+-----------------------------------------+--------------------------------------------+
| <Element 'country' at 0x0000000003C6C060> | <Element 'gdppc' at 0x0000000003C6C0F0> | <Element 'neighbor' at 0x0000000003C6C1E0> |
+-------------------------------------------+-----------------------------------------+--------------------------------------------+

>>> # xml with namespace
>>> element = etree.fromstring("""<f:table xmlns:f="http://www.w3school.com.cn/furniture">
...                                 <f:name>African Coffee Table</f:name>
...                                 <f:width>80</f:width>
...                                 <f:length>120</f:length>
...                         </f:table>""")
>>>
>>> node2 = xmlutil.XMLNode(element)
>>> nsmap = {'ns': node2.namespace()}   # namespace
>>> node2.find('.//{ns}name'.format(**nsmap)).to_table()
+------------------------+
| name                   |
+========================+
| 'African Coffee Table' |
+------------------------+

>>> node.findall('.//dataType').to_table()
+----------+
| dataType |
+==========+
| 'GDP'    |
+----------+

>>> node.findall('.//country').to_table()
+------+--------+----------+
| rank | year   | gdppc    |
+======+========+==========+
| '1'  | '2008' | '141100' |
+------+--------+----------+
| '4'  | '2011' | '59900'  |
+------+--------+----------+

>>> table_name = node2.find('.//{ns}name'.format(**nsmap))
>>> data_type_list = node.findall('.//dataType')
>>> countries = node.findall('.//country')
>>> table_name.crossjoin(data_type_list).to_table()
+------------------------+----------+
| name                   | dataType |
+========================+==========+
| 'African Coffee Table' | 'GDP'    |
+------------------------+----------+
>>> table_name.crossjoin(data_type_list).crossjoin(countries).to_table()
+----------+------------------------+------+--------+----------+
| dataType | name                   | rank | year   | gdppc    |
+==========+========================+======+========+==========+
| 'GDP'    | 'African Coffee Table' | '1'  | '2008' | '141100' |
+----------+------------------------+------+--------+----------+
| 'GDP'    | 'African Coffee Table' | '4'  | '2011' | '59900'  |
+----------+------------------------+------+--------+----------+

>>>
```
