#!/usr/bin/bash

sudo rm /media/pi/RetroNAS/mister/games/mame/*
sudo rm /media/pi/RetroNAS/mister/games/hbmame/*

rsync -av --progress /mnt/mister/games/hbmame/* /media/pi/RetroNAS/mister/games/hbmame/

rsync -av --progress /mnt/mister/games/mame/* /media/pi/RetroNAS/mister/games/mame/