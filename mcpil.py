#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  mcpil.py
#  
#  Copyright 2020 Alvarito050506 <donfrutosgomez@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import sys
import subprocess
import atexit
import signal
import webbrowser
import psutil
import time
from os import walk, remove, path, chdir, kill, rename, environ, uname, geteuid
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from shutil import copy2

descriptions = ["Miecraft Pi Edition. v0.1.1. Default game mode: Creative.", "Minecraft Pocket Edition. v0.6.1. Default game mode: Survival."];
binaries = ["minecraft-pi", "minecraft-pe"];

def on_select_versions(event):
	global current_selection;
	description_text["text"] = descriptions[int(event.widget.curselection()[0])];
	current_selection = int(event.widget.curselection()[0]);
	return 0;

def launch():
	global mcpi_pid;
	mcpi_process = subprocess.Popen([binaries[current_selection]]);
	time.sleep(2);
	mcpi_pid = mcpi_process.pid + 2;
	start_mods();
	return 0;

def save_settings():
	username = username_entry.get();
	i = 0;

	while len(username) < 7:
		username = username + "\x00";

	mcpi_file = open("/opt/minecraft-pi/minecraft-pi", "r+");
	mcpi_file.seek(0xfa8ca);
	while i < 7:
		mcpi_file.write(username[i]);
		i += 1;
	i = 0;
	mcpi_file.close();

	mcpe_file = open("/opt/minecraft-pi/minecraft-pe", "r+");
	mcpe_file.seek(0xfa8ca);
	while i < 7:
		mcpe_file.write(username[i]);
		i += 1;
	mcpe_file.close();
	return 0;

def on_select_mods(event):
	if mods.get(int(event.widget.curselection()[0])) is not None:
		delete_button["state"] = NORMAL;
	else:
		delete_button["state"] = DISABLED;
	return 0;

def install_mod(mod_file=None):
	if mod_file is None:
		mod_file = askopenfilename(filetypes=[("Minecraft Pi Mods", "*.mcpi *.py")]);
	copy2(mod_file, "./mods/" + path.basename(mod_file));
	update_mods();
	delete_button["state"] = DISABLED;
	return 0;

def delete_mod():
	remove("./mods/" + mods.get(int(mods.curselection()[0])));
	update_mods();
	delete_button["state"] = DISABLED;
	return 0;

def update_mods():
	mod_files = [];
	i = 0;

	for (_, _, files) in walk("mods"):
		mod_files.extend(files);

	mods.delete(0, END);

	while i < len(mod_files):
		mods.insert(i, mod_files[i].replace(".py", "").replace(".mcpi", ""));
		i += 1;
	return 0;

def start_mods():
	global mods_process;
	mods_env = environ.copy();
	mcpi_file = open("/opt/minecraft-pi/minecraft-pi", "rb");
	mcpi_file.seek(0xfa8ca);
	mods_env["MCPIL_USERNAME"] = mcpi_file.read(7).decode("utf-8");
	mcpi_file.close();
	mods_env["MCPIL_PID"] = str(mcpi_pid);
	mods_process = subprocess.Popen(["./mcpim.py"], env=mods_env);
	return 0;

def kill_mods():
	kill(mods_process.pid, signal.SIGTERM);
	return 0;

def change_skin():
	skin_file = askopenfilename(filetypes=[("Portable Network Graphics", "*.png")]);
	copy2("/opt/minecraft-pi/data/images/mob/char.png", "/opt/minecraft-pi/data/images/mob/char_original.png");
	copy2(skin_file, "/opt/minecraft-pi/data/images/mob/char.png");
	return 0;

def web_open(event):
	webbrowser.open(event.widget.cget("text"));
	return 0;

def save_world():
	old_world_name = old_worldname_entry.get();
	new_world_name = new_worldname_entry.get();
	world_file = open("/root/.minecraft/games/com.mojang/minecraftWorlds/" + old_world_name + "/level.dat", "rb+");
	new_world = world_file.read().replace(bytes([len(old_world_name)]) + bytes([0]) + bytes(old_world_name.encode()), bytes([len(new_world_name)]) + bytes([0]) + bytes(new_world_name.encode()));
	world_file.seek(0);
	world_file.write(new_world);
	world_file.seek(0x16);
	world_file.write(bytes([game_mode.get()]));
	world_file.close();
	rename("/root/.minecraft/games/com.mojang/minecraftWorlds/" + old_world_name, "/root/.minecraft/games/com.mojang/minecraftWorlds/" + new_world_name);
	return 0;

def set_default_worldname(event):
	new_worldname_entry.delete(0, END);
	new_worldname_entry.insert(0, old_worldname_entry.get());
	return True;

def add_server():
	global proxy_process;
	server_addr = server_addr_entry.get();
	server_port = server_port_entry.get();
	proxy_process = subprocess.Popen(["./mcpip.py", server_addr, server_port]);
	return 0;

def kill_proxy():
	try:
		kill(proxy_process.pid, signal.SIGTERM);
	except NameError:
		pass;
	return 0;

def play_tab(parent):
	global description_text;

	tab = Frame(parent);

	title = Label(tab, text="Minecraft Pi Launcher");
	title.config(font=("", 24));
	title.pack();

	choose_text = Label(tab, text="Choose a Minecraft version to launch.");
	choose_text.pack(pady=16);

	versions_frame = Frame(tab);
	versions = Listbox(versions_frame, selectmode=SINGLE, width=22);
	versions.insert(0, " Minecraft Pi Edition ");
	versions.insert(1, " Minecraft Pocket Edition ");
	versions.bind('<<ListboxSelect>>', on_select_versions);
	versions.pack(side=LEFT);

	description_text = Label(versions_frame, text="", wraplength=256);
	description_text.pack(pady=48);

	versions_frame.pack(fill=BOTH, expand=True);

	launch_frame = Frame(tab);
	launch_button = Button(launch_frame, text="Launch!", command=launch);
	launch_button.pack(side=RIGHT, anchor=S);
	launch_frame.pack(fill=BOTH, expand=True);
	return tab;

def settings_tab(parent):
	global username_entry;
	tab = Frame(parent);

	title = Label(tab, text="Settings");
	title.config(font=("", 24));
	title.pack();

	form_frame = Frame(tab);
	username_text = Label(form_frame, text="Username (7 characters max):");
	username_text.pack(side=LEFT, anchor=N, pady=16, padx=8);

	username_entry = Entry(form_frame, width=32);
	username_entry.pack(side=RIGHT, anchor=N, pady=16, padx=8);
	form_frame.pack(fill=X);

	buttons_frame = Frame(tab);
	skin_button = Button(buttons_frame, text="Change skin", command=change_skin);
	skin_button.pack(side=LEFT, anchor=S);
	save_button = Button(buttons_frame, text="Save", command=save_settings);
	save_button.pack(side=RIGHT, anchor=S);
	buttons_frame.pack(fill=BOTH, expand=True);
	return tab;

def mods_tab(parent):
	global delete_button;
	global mods;
	tab = Frame(parent);

	title = Label(tab, text="Mods");
	title.config(font=("", 24));
	title.pack();

	mods_frame = Frame(tab);
	mods = Listbox(mods_frame, selectmode=SINGLE, width=22);
	update_mods();
	mods.bind('<<ListboxSelect>>', on_select_mods);
	mods.pack(pady=16);
	mods_frame.pack();

	buttons_frame = Frame(tab);
	start_button = Button(buttons_frame, text="Start mods", command=start_mods);
	start_button.pack(side=RIGHT, anchor=S);
	install_button = Button(buttons_frame, text="Install", command=install_mod);
	install_button.pack(side=RIGHT, anchor=S);
	delete_button = Button(buttons_frame, text="Delete", command=delete_mod, state=DISABLED);
	delete_button.pack(side=RIGHT, anchor=S);
	buttons_frame.pack(fill=BOTH, expand=True);
	return tab;

def worlds_tab(parent):
	global old_worldname_entry;
	global new_worldname_entry;
	global game_mode;
	tab = Frame(parent);

	title = Label(tab, text="Worlds");
	title.config(font=("", 24));
	title.pack();

	old_worldname_frame = Frame(tab);
	old_worldname_text = Label(old_worldname_frame, text="World Name:");
	old_worldname_text.pack(side=LEFT, anchor=N, pady=16, padx=8);

	old_worldname_entry = Entry(old_worldname_frame, width=32, validate="focus", validatecommand=(tab.register(set_default_worldname), "%P"));
	old_worldname_entry.pack(side=RIGHT, anchor=N, pady=16, padx=8);
	old_worldname_frame.pack(fill=X);

	new_worldname_frame = Frame(tab);
	new_worldname_text = Label(new_worldname_frame, text="New World Name:");
	new_worldname_text.pack(side=LEFT, anchor=N, padx=8);

	new_worldname_entry = Entry(new_worldname_frame, width=32);
	new_worldname_entry.pack(side=RIGHT, anchor=N, padx=8);
	new_worldname_frame.pack(fill=X);

	game_mode_frame = Frame(tab);
	game_mode_text = Label(game_mode_frame, text="Game mode:");
	game_mode_text.pack(side=LEFT, anchor=N, pady=16, padx=8);
	game_mode = IntVar();
	game_mode.set(1);
	survival_mode_button = Radiobutton(game_mode_frame, text="Survival", variable=game_mode, value=0, indicatoron=False, width=12);
	creative_mode_button = Radiobutton(game_mode_frame, text="Creative", variable=game_mode, value=1, indicatoron=False, width=12);
	creative_mode_button.pack(side=RIGHT, pady=16, padx=8);
	survival_mode_button.pack(side=RIGHT, pady=16, padx=8);
	game_mode_frame.pack(fill=X);

	buttons_frame = Frame(tab);
	start_button = Button(buttons_frame, text="Save", command=save_world);
	start_button.pack(side=RIGHT, anchor=S);
	buttons_frame.pack(fill=BOTH, expand=True);
	return tab;

def servers_tab(parent):
	global server_addr_entry;
	global server_port_entry;
	tab = Frame(parent);

	title = Label(tab, text="Servers");
	title.config(font=("", 24));
	title.pack();

	server_addr_frame = Frame(tab);
	server_addr_text = Label(server_addr_frame, text="Server addres:");
	server_addr_text.pack(side=LEFT, anchor=N, pady=16, padx=8);

	server_addr_entry = Entry(server_addr_frame, width=32);
	server_addr_entry.pack(side=RIGHT, anchor=N, pady=16, padx=8);
	server_addr_frame.pack(fill=X);

	server_port_frame = Frame(tab);
	server_port_text = Label(server_port_frame, text="Server port:");
	server_port_text.pack(side=LEFT, anchor=N, padx=8);

	server_port_entry = Entry(server_port_frame, width=32);
	server_port_entry.pack(side=RIGHT, anchor=N, padx=8);
	server_port_frame.pack(fill=X);

	buttons_frame = Frame(tab);
	start_button = Button(buttons_frame, text="Add server", command=add_server);
	start_button.pack(side=RIGHT, anchor=S);
	buttons_frame.pack(fill=BOTH, expand=True);
	return tab;

def about_tab(parent):
	tab = Frame(parent);

	title = Label(tab, text="Minecraft Pi Launcher");
	title.config(font=("", 24));
	title.pack();

	version = Label(tab, text="v0.2.0");
	version.config(font=("", 10));
	version.pack();

	author = Label(tab, text="by @Alvarito050506");
	author.config(font=("", 10));
	author.pack();
	author.bind("<Button-1>", web_open);

	url = Label(tab, text="https://github.com/Alvarito050506/MCPIL", fg="blue", cursor="hand2");
	url.config(font=("", 10));
	url.pack();
	author.bind("<Button-1>", web_open);
	return tab;

def main(args):
	if "arm" not in uname()[4] and "aarch" not in uname()[4]:
		sys.stdout.write("Error: Minecraft Pi Launcher must run on a Raspberry Pi.\n");
		return 1;

	if geteuid() != 0:
		sys.stdout.write("Error: You need to have root privileges to run this program.\n");
		return 1;

	global mods_process;
	chdir(path.dirname(__file__));
	window = Tk();
	window.title("MCPI Laucher");
	window.geometry("480x348");
	window.resizable(False, False);
	window.iconphoto(True, PhotoImage(file="./.install_files/icon.png"))

	tabs = ttk.Notebook(window);
	tabs.add(play_tab(tabs), text="Play");
	tabs.add(settings_tab(tabs), text="Settings");
	tabs.add(mods_tab(tabs), text="Mods");
	tabs.add(worlds_tab(tabs), text="Worlds");
	tabs.add(servers_tab(tabs), text="Servers");
	tabs.add(about_tab(tabs), text="About");
	tabs.pack(fill=BOTH, expand=True);

	if len(args) > 1:
		install_mod(args[1]);

	atexit.register(kill_mods);
	atexit.register(kill_proxy);

	window.mainloop();
	return 0;

if __name__ == '__main__':
	sys.exit(main(sys.argv));
