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
    raise ValueError('Invalid code point')

def texify(s: str):
    replace = {'&': '\\&', '#': '\\#', '’': '\'', '“': '``', '”': '\'\'', ' ': '~'}
    for k, v in replace.items():
        s = s.replace(k, v)
    return s[0].capitalize() + s[1:]

class Builder:
    def __init__(self):
        self.emoji: dict[str, dict[str, list]] = {}
        self.emoji_names: set[str] = set()
        self.github_data: dict[str, list[str]] = {}
        self.github_hex_data: dict[str, list[str]] = {}
        self._read_from_unicode_data()
        self._read_from_github_data()
        self._normalize()
        self._remove_duplicates()

    def _read_from_unicode_data(self):
        with open(UNICODE_EMOJI_DATA_FILE, encoding='utf-8') as f:
            for line in f.readlines():
                if line.startswith('# group'):
                    group_name = line[9:-1]
                    self.emoji[group_name] = {}
                elif line.startswith('# subgroup'):
                    subgroup_name = line[12:-1]
                    self.emoji[group_name][subgroup_name] = []
                elif not line.startswith('#') and line != '\n':
                    entry = re.findall(EMOJI_ENTRY_PATTERN, line)
                    if entry:
                        self.emoji[group_name][subgroup_name].append(entry[0])

    def _read_from_github_data(self):
        with open(GITHUB_EMOJI_DATA_FILE, encoding='utf-8') as f:
            for i in json.load(f):
                self.github_data[i['description']] = i['aliases']
                self.github_hex_data[to_code_points(i['emoji'])] = i['aliases']

    def _normalize(self):
        for group in self.emoji.values():
            for subgroup_name, subgroup in group.items():
                entries = []
                for item in subgroup:
                    (code_points, version, description) = (item[0], item[1], item[2])
                    name = normalize_name(description)
                    aliases = (
                        self.github_hex_data.get(code_points, []) +
                        self.github_data.get(description, [])
                    )
                    self.emoji_names.add(name)
                    entries.append({
                        'code_points': to_tex_code_points(code_points.split()),
                        'name': name,
                        'aliases': aliases,
                        'version': version,
                        'description': description,
                    })
                group[subgroup_name] = entries

    def _remove_duplicates(self):
        # The aliases should be distinct from all the emoji names and previous aliases
        previous_aliases = set()
        for group in self.emoji.values():
            for subgroup in group.values():
                for item in subgroup:
                    aliases = normalize_aliases(item['aliases'], self.emoji_names, previous_aliases)
                    previous_aliases.update(aliases)
                    item['aliases'] = ', '.join(aliases)

    def write(self):
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.writelines([
                COPYRIGHT_NOTICE,
                f'\\ProvidesExplFile{{{OUTPUT_FILE}}}\n',
                f'  {OUTPUT_FILE_INFO}\n',
            ])
            for group_name, group in self.emoji.items():
                f.write(f'\\__emoji_group:n {{{texify(group_name)}}}\n')
                for subgroup_name, subgroup in group.items():
                    f.write(f'\\__emoji_subgroup:n {{{texify(subgroup_name)}}}\n')
                    f.writelines(
                        ('\\__emoji_def:nnnnn' + ' {{{}}}' * 5).format(
                            item['code_points'],
                            item['name'],
                            item['aliases'],
                            texify(item['description']),
                            item['version']
                        ) + '\n'
                        for item in subgroup
                    )
            f.write(f'%%\n%% End of file `{OUTPUT_FILE}\'.\n')

if __name__ == '__main__':
    Builder().write()
