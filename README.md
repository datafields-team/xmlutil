# xmlutil
this package extrats data from xml tree with bfs algorithm and transforms data into a table with petl.<br />
it depends on packages ``xml.etree`` or ``lxml.etree`` and ``petl``.<br />

# find with xpath/relate/extract
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
>>> node = xmlutil.parse('country.xml')  # or xmlutil.XMLNode(element)
>>> country = node.find('.//country')
>>> table = country.to_table() 
>>> table
+------+--------+----------+
| rank | year   | gdppc    |
+======+========+==========+
| '1'  | '2008' | '141100' |
+------+--------+----------+
>>> country.to_dicts()
[OrderedDict([('rank', '1'), ('year', '2008'), ('gdppc', '141100')])]
>>> for dic in table.dicts():
...     print dic
...
{u'gdppc': '141100', u'rank': '1', u'year': '2008'}
>>> country.to_table(with_attrib=True)
+---------------------------+------+--------+----------+-------------------------------------------+
| country                   | rank | year   | gdppc    | neighbor                                  |
+===========================+======+========+==========+===========================================+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+------+--------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '1'  | '2008' | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+------+--------+----------+-------------------------------------------+
>>> country.to_table(with_attrib=True, exclusive_tags=('rank', 'year',))
+---------------------------+----------+-------------------------------------------+
| country                   | gdppc    | neighbor                                  |
+===========================+==========+===========================================+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'E', 'name': 'Austria'}     |
+---------------------------+----------+-------------------------------------------+
| {'name': 'Liechtenstein'} | '141100' | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+----------+-------------------------------------------+
>>> country.to_table(with_attrib=True, exclusive_tags=('gdppc', 'rank', 'year',), duplicate_tags=('neighbor',))
+---------------------------+---------------------------------------+-------------------------------------------+
| country                   | neighbor                              | neighbor_1                                |
+===========================+=======================================+===========================================+
| {'name': 'Liechtenstein'} | {'direction': 'E', 'name': 'Austria'} | {'direction': 'W', 'name': 'Switzerland'} |
+---------------------------+---------------------------------------+-------------------------------------------+

>>> country.to_table(with_attrib=True, exclusive_tags=('rank', 'year',), with_element=True)
+--------------------------------+------------------------------+---------------------------------+
| country                        | gdppc                        | neighbor                        |
+================================+==============================+=================================+
| <Element country at 0x3b50c88> | <Element gdppc at 0x3b40508> | <Element neighbor at 0x3b40208> |
+--------------------------------+------------------------------+---------------------------------+
| <Element country at 0x3b50c88> | <Element gdppc at 0x3b40508> | <Element neighbor at 0x3b40188> |
+--------------------------------+------------------------------+---------------------------------+

>>> # xml with namespace
>>> element = etree.fromstring("""<f:table xmlns=http://www.w3school.com.cn/xmlns xmlns:f="http://www.w3school.com.cn/furniture">
...                                 <f:name>African Coffee Table</f:name>
...                                 <f:width>80</f:width>
...                                 <f:length>120</f:length>
...                         </f:table>""")
>>>
>>> node2 = xmlutil.XMLNode(element)
>>> nsmap = {'ns': node2.namespace()}  
>>> node2.nsmap()
{None: 'http://www.w3school.com.cn/xmlns', 'f': 'http://www.w3school.com.cn/furniture'}
>>> node2.nsmap(sub='rename_default_ns')
{'rename_default_ns': 'http://www.w3school.com.cn/xmlns', 'f': 'http://www.w3school.com.cn/furniture'}
>>>
>>> node2.find('.//{ns}name'.format(**nsmap)).to_table()
+------------------------+
| name                   |
+========================+
| 'African Coffee Table' |
+------------------------+
>>>
>>> # relates multiple nodes
>>> xmlutil.EmptyNode().crossjoin(node.findall('.//country')).to_table()
+------+--------+----------+
| rank | year   | gdppc    |
+======+========+==========+
| '1'  | '2008' | '141100' |
+------+--------+----------+
| '4'  | '2011' | '59900'  |
+------+--------+----------+
>>> empty = xmlutil.EmptyNode()
>>> for country in node.findall('.//country'):
...     empty = empty.crossjoin(country)
...
>>> empty.to_table()
+----------+------+--------+------+--------+---------+
| gdppc    | rank | year   | rank | year   | gdppc   |
+==========+======+========+======+========+=========+
| '141100' | '1'  | '2008' | '4'  | '2011' | '59900' |
+----------+------+--------+------+--------+---------+
>>> table_name = node2.find('.//{ns}name'.format(**nsmap))
>>> data_type_list = node.findall('.//dataType')
>>> countries = node.findall('.//country')
>>> 
>>> related1 = table_name.crossjoin(data_type_list)
>>> related2 = table_name.crossjoin(data_type_list).crossjoin(countries)
>>> related1.to_table()
+------------------------+----------+
| name                   | dataType |
+========================+==========+
| 'African Coffee Table' | 'GDP'    |
+------------------------+----------+

>>> related2.to_table()
+----------+------------------------+------+--------+----------+
| dataType | name                   | rank | year   | gdppc    |
+==========+========================+======+========+==========+
| 'GDP'    | 'African Coffee Table' | '1'  | '2008' | '141100' |
+----------+------------------------+------+--------+----------+
| 'GDP'    | 'African Coffee Table' | '4'  | '2011' | '59900'  |
+----------+------------------------+------+--------+----------+

>>> related1.join(related2, key=('dataType', 'name')).to_table()
+----------+------------------------+----------+------+--------+
| dataType | name                   | gdppc    | rank | year   |
+==========+========================+==========+======+========+
| 'GDP'    | 'African Coffee Table' | '141100' | '1'  | '2008' |
+----------+------------------------+----------+------+--------+
| 'GDP'    | 'African Coffee Table' | '59900'  | '4'  | '2011' |
+----------+------------------------+----------+------+--------+

>>>
```
