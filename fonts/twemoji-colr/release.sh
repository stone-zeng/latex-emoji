#!/bin/sh

working_dir=$PWD
tmp_dir=/tmp/twemoji-colr
tds_dir=$tmp_dir/tds
ctan_dir=$tmp_dir/twemoji-colr
fonts_dir=$tds_dir/fonts/truetype/public/twemoji-colr
doc_dir=$tds_dir/doc/fonts/twemoji-colr

mkdir -p $tmp_dir
mkdir -p $tds_dir
mkdir -p $ctan_dir
mkdir -p $fonts_dir
mkdir -p $doc_dir

cp *.ttf     $ctan_dir
cp README.md $ctan_dir

chmod 644 $ctan_dir/*.*

cp $ctan_dir/*.ttf     $fonts_dir
cp $ctan_dir/README.md $doc_dir

cd $tds_dir
zip -q -r -9 twemoji-colr.tds.zip .

cp $tds_dir/*.zip $tmp_dir
rm -r $tds_dir

cd $tmp_dir
zip -q -r -9 twemoji-colr.zip .

cd $working_dir
cp -f $tmp_dir/twemoji-colr.zip     .
cp -f $tmp_dir/twemoji-colr.tds.zip .

rm -r $tmp_dir
