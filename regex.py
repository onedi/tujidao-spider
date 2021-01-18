# !/usr/bin/pyhton
import re
s = '/a/?id=33422'
r = re.search(r'id=(?P<id>\d+)',s)
print(r.groupdict())