#!/usr/bin/python3.7

#
# Entity Encoding to help prevent XSS
#
def entity_encode(s):
	escapes = {
		'&': '&amp;',
		"'": '&apos;',
		'"': '&quot;',
		'<': '&lt;',
		'>': '&gt;'
	}
	return "".join(escapes.get(c,c) for c in s)
