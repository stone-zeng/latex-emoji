#!/bin/sh

latexmk -pdflua -lualatex=lualatex-dev emoji-doc.tex

working_dir=$PWD
tmp_dir=/tmp/emoji
tds_dir=$tmp_dir/tds
ctan_dir=$tmp_dir/emoji
tex_dir=$tds_dir/tex/latex/emoji
doc_dir=$tds_dir/doc/latex/emoji

mkdir -p $tmp_dir
mkdir -p $tds_dir
mkdir -p $ctan_dir
mkdir -p $tex_dir
mkdir -p $doc_dir

cp emoji.sty     $ctan_dir
cp emoji-doc.tex $ctan_dir
cp emoji-doc.pdf $ctan_dir
cp README.md     $ctan_dir

chmod 644 $ctan_dir/*.*

cp $ctan_dir/emoji.sty     $tex_dir
cp $ctan_dir/emoji-doc.tex $doc_dir
cp $ctan_dir/emoji-doc.pdf $doc_dir
cp $ctan_dir/README.md     $doc_dir

cd $tds_dir
zip -q -r -9 emoji.tds.zip .

cp $tds_dir/*.zip $tmp_dir
rm -r $tds_dir

cd $tmp_dir
zip -q -r -9 emoji.zip .

cd $working_dir
mkdir -p ./release
cp -f $tmp_dir/emoji.zip     ./release
cp -f $tmp_dir/emoji.tds.zip ./release

rm -r $tmp_dir
