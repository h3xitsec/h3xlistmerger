#!/usr/bin/env python
import yaml
import requests
import re
import os

source_file = "./sources.yml"
list_dest = "/home/h3x/work/wordlists"
custom_lists_path = "./custom_lists"
list_folder = 'h3x'

sources = yaml.load(open(source_file,"r"), Loader=yaml.FullLoader)

print("Wordlists Merger")

def remove_duplicates(a):
    s = set()
    r = []
    for l in a:
        if l not in s:
            s.add(l)
            r.append(l)
    return r

def filter_list(a, p):
    f = []
    for l in a:
        if p.search(l):
            f.append(l)
    return f

def replace_list(a,p,r):
    f = []
    for l in a:
        f.append(re.sub(p, r, l))
    return f

## Fetch and merge wordlists
# iterate through the keys of sources file
for source_type in sources.keys():
    print(f"  Processing {source_type}")
    source = sources[source_type]
    if "regex" in source.keys():
        list_regex = re.compile(source['regex'])
    else:
        list_regex = None
    if "replace" in source.keys():
        list_replace = source["replace"]
    else:
        list_replace = None
    all_lines = []
    
    # fetch each urls in sources and apply source regex
    # source regex is applied only on the items from this source, not the whole list
    if "sources" in source.keys():
        for surl in source['sources']:
            if "regex" in surl.keys() and not surl['regex'] == "" and not surl['regex'] == None:
                source_regex = re.compile(surl['regex'])
            else:
                source_regex = ""
            url = surl['url']
            print(f"    {url}")
            lines_seen = set()
            if url.startswith('http'):
                lines = remove_duplicates(requests.get(url).text.splitlines())
            else:
                lines = remove_duplicates(open(url,"r").read().splitlines())
            # Apply source regex filter
            if not source_regex == "":
                print(f"      Applying source regex: \"{source_regex.pattern}\" ... ", end='')
                lines = filter_list(lines, source_regex)
                print(f"{len(lines)} matches")
            all_lines += lines
    
    # Load custom list if file exists
    if os.path.exists(f"{custom_lists_path}/{source_type}.txt"):
        print(f"    Appending custom list")
        all_lines += remove_duplicates(open(f"{custom_lists_path}/{source_type}.txt","r").read().splitlines())
    
    if list_replace:
        print(f"    Applying list replacement(s)")
        for rep in list_replace:
            all_lines = replace_list(all_lines, rep['pattern'], rep['replacement'])

    if list_regex:
        print(f"    Applying list regex")
        all_lines = filter_list(all_lines, list_regex)
    
    with open(f"{list_dest}/{list_folder}/{source_type}.txt","w") as list_file:
        for line in remove_duplicates(all_lines):
            # remove comments from lists
            if not re.compile(r'^\#').match(line):
                list_file.write(f"{line}\n")
        list_file.close()

