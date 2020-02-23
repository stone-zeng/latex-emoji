# The `emoji` package

[![CTAN](https://img.shields.io/ctan/v/emoji.svg)](https://www.ctan.org/pkg/emoji)
[![GitHub release](https://img.shields.io/github/release/stone-zeng/latex-emoji/all.svg)](https://github.com/stone-zeng/latex-emoji/releases/latest)

Emoji support in (Lua)LaTeX.

## Introduction

The `emoji` package allows user to typeset emoji in a LaTeX document. It requires LuaHBTeX, or `lualatex-dev` at present.

## Usage

```tex
\documentclass{article}
\usepackage{emoji}
\setemojifont{Apple Color Emoji}  % Optional

\begin{document}
\emoji{joy}
\emoji{+1}
\emoji{family-man-woman-girl-boy}
\end{document}
```

Result:

> &#x1F602;
> &#x1F44D;
> &#x1F468;&#x200D;&#x1F469;&#x200D;&#x1F467;&#x200D;&#x1F466;

## License

This work may be distributed and/or modified under the conditions of the [LaTeX Project Public License](http://www.latex-project.org/lppl.txt), either version 1.3c of this license or (at your option) any later version.

-----

Copyright (C) 2020 by Xiangdong Zeng.
