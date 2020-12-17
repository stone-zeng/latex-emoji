# -*- coding: utf-8 -*-

import json
import re
import unicodedata as ud
from typing import List

COPYRIGHT_NOTICE = r"""%%
%%  Copyright (C) 2020 by Xiangdong Zeng <xdzeng96@gmail.com>
%%
%%  This work may be distributed and/or modified under the
%%  conditions of the LaTeX Project Public License, either
%%  version 1.3c of this license or (at your option) any later
%%  version. The latest version of this license is in:
%%
%%    http://www.latex-project.org/lppl.txt
%%
%%  and version 1.3 or later is part of all distributions of
%%  LaTeX version 2005/12/01 or later.
%%
%%  This work has the LPPL maintenance status `maintained'.
%%
%%  The Current Maintainer of this work is Xiangdong Zeng.
%%
"""

UNICODE_EMOJI_DATA_FILE = './data/emoji-test.txt'
GITHUB_EMOJI_DATA_FILE = './data/emoji.json'

OUTPUT_FILE = 'emoji-table.def'
OUTPUT_FILE_INFO = '{2020/06/27}{0.2.1}{Emoji support in (Lua)LaTeX}'

# 0 = code points, 1 = version, 2 = description
EMOJI_ENTRY_PATTERN = re.compile(r'^(.+?)\W+;\W(?:fully-qualified|component).+E(\d+\.\d+)\W+(.+)')

def texify(s: str):
    replace = {'&': '\\&', '#': '\\#', '’': "'", '“': "``", '”': "''", ' ': '~'}
    for k, v in replace.items():
        s = s.replace(k, v)
    return s[0].capitalize() + s[1:]

def normalize_name(s: str):
    # Remove accents.
    s = ''.join(c for c in ud.normalize('NFD', s.lower()) if ud.category(c) != 'Mn')
    s = re.sub(r',|\.|:|\(|\)|’|“|”|&', '', s)
    s = re.sub(r'\s+', '-', s)
    return s.replace('#', 'hash').replace('*', 'asterisk')

def normalize_aliases(name: str, names: List[str], raw_aliases: List[str]):
    aliases = []
    if raw_aliases[0] is not None:
        aliases = raw_aliases[0]
    if raw_aliases[1] is not None:
        aliases += raw_aliases[1]
    aliases = sorted(set(aliases))
    if not aliases:
        return ''
    aliases = [s.replace('_', '-') for s in aliases]
    return ', '.join([s for s in aliases if s != name and s not in names])

def to_tex_code_points(c_list: List[str]):
    return ''.join([to_tex_hex(c) for c in c_list]).lower()

def to_tex_hex(s: str):
    if len(s) == 4:
        return '^^^^' + s
    if len(s) == 5:
        return '^^^^^^0' + s

def to_code_points(s: str):
    return ' '.join([hex(ord(i))[2:].upper() for i in s])

with open(UNICODE_EMOJI_DATA_FILE) as f:
    emoji = dict()
    for line in f.readlines():
        if line.startswith('# group'):
            group_name = line[9:-1]
            emoji[group_name] = dict()
        elif line.startswith('# subgroup'):
            subgroup_name = line[12:-1]
            emoji[group_name][subgroup_name] = []
        elif not line.startswith('#') and line != '\n':
            entry = re.findall(EMOJI_ENTRY_PATTERN, line)
            if entry:
                emoji[group_name][subgroup_name].append(entry[0])

with open(GITHUB_EMOJI_DATA_FILE) as f:
    github_data = {}
    github_hex_data = {}
    for i in json.load(f):
        github_data[i['description']] = i['aliases']
        github_hex_data[to_code_points(i['emoji'])] = i['aliases']

emoji_names = []
for i in emoji:
    for j in emoji[i]:
        entries = []
        for k in emoji[i][j]:
            (code_points, version, description) = (k[0], k[1], k[2])
            name = normalize_name(description)
            entries.append({
                'code_points': to_tex_code_points(code_points.split()),
                'name': name,
                'aliases': [github_hex_data.get(code_points), github_data.get(description)],
                'version': version,
                'description': description})
            emoji_names.append(name)
        emoji[i][j] = entries

# Remove duplicated aliases.
for i in emoji:
    for j in emoji[i]:
        for k in emoji[i][j]:
            k['aliases'] = normalize_aliases(k['name'], emoji_names, k['aliases'])

with open(OUTPUT_FILE, 'w') as f:
    f.writelines(COPYRIGHT_NOTICE)
    f.writelines(r'\ProvidesExplFile{{{}}}'.format(OUTPUT_FILE) + '\n')
    f.writelines('  ' + OUTPUT_FILE_INFO + '\n')
    for i in emoji:
        f.writelines(r'\__emoji_group:n {' + texify(i) + '}\n')
        for j in emoji[i]:
            f.writelines(r'\__emoji_subgroup:n {' + texify(j) + '}\n')
            for k in emoji[i][j]:
                line = (r'\__emoji_def:nnnnn' + ' {{{}}}' * 5).format(
                    k['code_points'],
                    k['name'],
                    k['aliases'],
                    texify(k['description']),
                    k['version']
                )
                f.writelines(line + '\n')
    f.writelines("%%\n%% End of file `{}'.\n".format(OUTPUT_FILE))
