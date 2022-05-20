import re
text = "This is some nice text"
iter_matches = re.finditer(".*\s", text)
for match in iter_matches:
    print(match.group(0))