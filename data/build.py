# -*- coding: utf-8 -*-

import json
import re
import unicodedata as ud

COPYRIGHT_NOTICE = r'''%%
%%  Copyright (C) 2020--2022 by Xiangdong Zeng <xdzeng96@gmail.com>
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
'''

UNICODE_EMOJI_DATA_FILE = './data/emoji-test.txt'
GITHUB_EMOJI_DATA_FILE = './data/emoji.json'

OUTPUT_FILE = 'emoji-table.def'
OUTPUT_FILE_INFO = '{2021/07/17}{0.2.2}{Emoji support in (Lua)LaTeX}'

# 0 = code points, 1 = version, 2 = description
EMOJI_ENTRY_PATTERN = re.compile(r'^(.+?)\W+;\W(?:fully-qualified|component).+E(\d+\.\d+)\W+(.+)')

def to_code_points(s: str):
    return ' '.join([hex(ord(i))[2:].upper() for i in s])

def normalize_name(s: str):
    # Remove accents
    s = ''.join(c for c in ud.normalize('NFD', s.lower()) if ud.category(c) != 'Mn')
    s = re.sub(r',|\.|:|\(|\)|’|“|”|&', '', s)
    s = re.sub(r'\s+', '-', s)
    return s.replace('#', 'hash').replace('*', 'asterisk')

def normalize_aliases(aliases: list[str], names: set[str], previous_aliases: set[str]):
    return sorted(set(s.replace('_', '-') for s in aliases) - (names | previous_aliases))

def to_tex_code_points(c_list: list[str]):
    return ''.join(to_tex_hex(c) for c in c_list).lower()

def to_tex_hex(s: str):
    if len(s) == 4:
        return '^^^^' + s
    if len(s) == 5:
        return '^^^^^^0' + s

def texify(s: str):
    replace = {'&': '\\&', '#': '\\#', '’': '\'', '“': '``', '”': '\'\'', ' ': '~'}
    for k, v in replace.items():
        s = s.replace(k, v)
    return s[0].capitalize() + s[1:]

# Read from Unicode data
with open(UNICODE_EMOJI_DATA_FILE) as f:
    emoji = {}
    for line in f.readlines():
        if line.startswith('# group'):
            group_name = line[9:-1]
            emoji[group_name] = {}
        elif line.startswith('# subgroup'):
            subgroup_name = line[12:-1]
            emoji[group_name][subgroup_name] = []
        elif not line.startswith('#') and line != '\n':
            entry = re.findall(EMOJI_ENTRY_PATTERN, line)
            if entry:
                emoji[group_name][subgroup_name].append(entry[0])

# Read from GitHub data
with open(GITHUB_EMOJI_DATA_FILE) as f:
    github_data = {}
    github_hex_data = {}
    for i in json.load(f):
        github_data[i['description']] = i['aliases']
        github_hex_data[to_code_points(i['emoji'])] = i['aliases']

# Normalize emoji data
emoji_names = set()
for i in emoji:
    for j in emoji[i]:
        entries = []
        for k in emoji[i][j]:
            (code_points, version, description) = (k[0], k[1], k[2])
            name = normalize_name(description)
            aliases = github_hex_data.get(code_points, []) + github_data.get(description, [])
            emoji_names.add(name)
            entries.append({
                'code_points': to_tex_code_points(code_points.split()),
                'name': name,
                'aliases': aliases,
                'version': version,
                'description': description,
            })
        emoji[i][j] = entries

# Remove duplicated aliases
# The aliases should be distinct from all the emoji names and previous aliases
previous_aliases = set()
for i in emoji:
    for j in emoji[i]:
        for k in emoji[i][j]:
            aliases = normalize_aliases(k['aliases'], emoji_names, previous_aliases)
            previous_aliases.update(aliases)
            k['aliases'] = ', '.join(aliases)

# Write into LaTeX file
with open(OUTPUT_FILE, 'w') as f:
    f.write(COPYRIGHT_NOTICE)
    f.write(f'\\ProvidesExplFile{{{OUTPUT_FILE}}}\n')
    f.write(f'  {OUTPUT_FILE_INFO}\n')
    for i in emoji:
        f.write(f'\\__emoji_group:n {{{texify(i)}}}\n')
        for j in emoji[i]:
            f.write(f'\\__emoji_subgroup:n {{{texify(j)}}}\n')
            for k in emoji[i][j]:
                line = ('\\__emoji_def:nnnnn' + ' {{{}}}' * 5).format(
                    k['code_points'],
                    k['name'],
                    k['aliases'],
                    texify(k['description']),
                    k['version']
                )
                f.write(line + '\n')
    f.write(f'%%\n%% End of file `{OUTPUT_FILE}\'.\n')
