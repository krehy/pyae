#!/bin/bash

# Vytvoří bin adresář, pokud neexistuje
mkdir -p bin

# Stáhne statickou FFmpeg binárku
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz

# Rozbalí
tar -xf ffmpeg.tar.xz

# Přesune do bin/
mv ffmpeg-*-static/ffmpeg bin/
mv ffmpeg-*-static/ffprobe bin/

# Nastaví spustitelnost
chmod +x bin/ffmpeg
chmod +x bin/ffprobe

# Uklidí
rm -rf ffmpeg.tar.xz ffmpeg-*-static
