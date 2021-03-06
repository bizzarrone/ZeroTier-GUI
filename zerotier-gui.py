#!/usr/bin/env python3
#
#A Linux front-end for ZeroTier
#Copyright (C) 2020  Tomás Ralph
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##################################
#                                #
#       Created by tralph3       #
#   https://github.com/tralph3   #
#                                #
##################################

import tkinter as tk
from tkinter import messagebox
from subprocess import check_output, STDOUT, CalledProcessError
from json import loads
from os import getuid, system, _exit
from webbrowser import open_new_tab

class MainWindow:

	def __init__(self):

		# create widgets
		# window setup
		self.window = tk.Tk()
		self.window.title("ZeroTier")
		self.window.resizable(width = False, height = False)

		# colors
		self.background = "#d9d9d9"
		self.foreground = "black"
		self.buttonBackground = "#ffb253"
		self.buttonActiveBackground = "#ffbf71"

		# layout setup
		self.topFrame = tk.Frame(self.window, padx = 20, pady = 10, bg=self.background)
		self.topBottomFrame = tk.Frame(self.window, padx = 20, bg=self.background)
		self.middleFrame = tk.Frame(self.window, padx = 20, bg=self.background)
		self.bottomFrame = tk.Frame(self.window, padx = 20, pady = 10, bg=self.background)

		# widgets
		self.networkLabel = tk.Label(self.topFrame, text="Joined Networks:", font=40, bg=self.background, fg=self.foreground)
		self.refreshButton = self.formatted_buttons(self.topFrame,
			text="Refresh Networks", command=self.refresh_networks)
		self.aboutButton = self.formatted_buttons(self.topFrame,
			text="About", command=self.about_window)
		self.peersButton = self.formatted_buttons(self.topFrame,
			text="Show Peers", command=self.see_peers)
		self.joinButton = self.formatted_buttons(self.topFrame,
			text="Join Network", command=self.join_network_window)

		self.tableLabels = tk.Label(self.topBottomFrame, font="Monospace",  bg="grey",
			text="{:19s}{:57s}{:26}".format("Network ID", "Name", "Status"), fg=self.foreground
		)

		self.networkListScrollbar = tk.Scrollbar(self.middleFrame, bd=2)

		self.networkList = tk.Listbox(self.middleFrame, width="100", height="15",
			font="Monospace", selectmode="single", relief="flat", bg="white", fg=self.foreground
		)

		self.networkList.bind('<Double-Button-1>', self.call_see_network_info)

		self.leaveButton = self.formatted_buttons(self.bottomFrame, text="Leave Network", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=self.leave_network
		)
		self.ztCentralButton = self.formatted_buttons(self.bottomFrame, text="ZeroTier Central", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=self.zt_central
		)
		self.toggleConnectionButton = self.formatted_buttons(self.bottomFrame, text="Disconnect/Connect Interface", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=self.toggle_interface_connection
		)
		self.infoButton = self.formatted_buttons(self.bottomFrame, text="Network Info", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=self.see_network_info
		)

		# pack widgets
		self.networkLabel.pack(side="left", anchor="sw")
		self.refreshButton.pack(side="right", anchor="se")
		self.aboutButton.pack(side="right", anchor="sw")
		self.peersButton.pack(side="right", anchor="sw")
		self.joinButton.pack(side="right", anchor="se")

		self.tableLabels.pack(side="left", fill="x")

		self.networkListScrollbar.pack(side="right", fill="both")
		self.networkList.pack(side="bottom", fill="x")

		self.leaveButton.pack(side="left", fill="x")
		self.toggleConnectionButton.pack(side="left", fill="x")
		self.infoButton.pack(side="right", fill="x")
		self.ztCentralButton.pack(side="right", fill="x")

		# frames
		self.topFrame.pack(side="top", fill="x")
		self.topBottomFrame.pack(side="top", fill="x")
		self.middleFrame.pack(side = "top", fill = "x")
		self.bottomFrame.pack(side = "top", fill = "x")

		# extra configuration
		self.refresh_networks()

		self.networkList.config(yscrollcommand=self.networkListScrollbar.set)
		self.networkListScrollbar.config(command=self.networkList.yview)

	def zt_central(self):
		open_new_tab("https://my.zerotier.com")

	def call_see_network_info(self, event):
		self.see_network_info()

	def refresh_paths(self, pathsList, idInList):

		pathsList.delete(0, 'end')
		paths = []
		# outputs info of paths in json format
		pathsData = self.get_peers_info()[idInList]['paths']

		# get paths information in a list of tuples
		for pathPosition in range(len(pathsData)):
			paths.append((
				pathsData[pathPosition]['active'],
				pathsData[pathPosition]['address'],
				pathsData[pathPosition]['expired'],
				pathsData[pathPosition]['lastReceive'],
				pathsData[pathPosition]['lastSend'],
				pathsData[pathPosition]['preferred'],
				pathsData[pathPosition]['trustedPathId']
			))

		# set paths in listbox
		for pathActive, pathAddress, pathExpired, pathLastReceive, pathLastSend, pathPreferred, pathTrustedId in paths:
			pathsList.insert('end', '{:6s} | {:44s} | {:7s} | {:13s} | {:13s} | {:9s} | {}'.format(
				str(pathActive),
				str(pathAddress),
				str(pathExpired),
				str(pathLastReceive),
				str(pathLastSend),
				str(pathPreferred),
				str(pathTrustedId)
			))

	def refresh_peers(self, peersList):

		peersList.delete(0, 'end')
		peers = []
		# outputs info of peers in json format
		peersData = self.get_peers_info()

		# get peers information in a list of tuples
		for peerPosition in range(len(peersData)):
			peers.append((
				peersData[peerPosition]['address'],
				peersData[peerPosition]['version'],
				peersData[peerPosition]['role'],
				peersData[peerPosition]['latency']
			))

		# set peers in listbox
		for peerAddress, peerVersion, peerRole, peerLatency in peers:

			if peerVersion == "-1.-1.-1":
				peerVersion = "-"
			peersList.insert('end', '{} | {:10s} | {:10s} | {:4s}'.format(
				peerAddress,
				peerVersion,
				peerRole,
				str(peerLatency)
			))

	def refresh_networks(self):

		self.networkList.delete(0, 'end')
		networks = []
		# outputs info of networks in json format
		networkData = self.get_networks_info()

		# gets networks information in a list of tuples
		for networkPosition in range(len(networkData)):

			interfaceState = self.get_interface_state(networkData[networkPosition]['portDeviceName'])

			if interfaceState.lower() == "down":
				isDown = True
			else:
				isDown = False

			networks.append((
				networkData[networkPosition]['id'],
				networkData[networkPosition]['name'],
				networkData[networkPosition]['status'],
				isDown,
				networkPosition
			))

		# set networks in listbox
		for networkId, networkName, networkStatus, isDown, networkPosition in networks:

			if not networkName:
				networkName = "No name"
			self.networkList.insert('end', '{} | {:55s} |{}'.format(
				networkId,
				networkName,
				networkStatus
			))

			if isDown:
				self.networkList.itemconfig(networkPosition, bg='red', selectbackground='#de0303')

	def get_networks_info(self):
		# json.loads
		return loads(check_output(['zerotier-cli', '-j', 'listnetworks']))

	def get_peers_info(self):
		# json.loads
		return loads(check_output(['zerotier-cli', '-j', 'peers']))

	def launch_sub_window(self, title):
		subWindow = tk.Toplevel(self.window)
		subWindow.title(title)
		subWindow.resizable(width = False, height = False)

		return subWindow

	# creates entry widgets to select and copy text
	def selectable_text(self, frame, text, justify="left", font="TkDefaultFont"):

		entry = tk.Entry(
			frame,
			relief="flat",
			bg=self.background,
			highlightcolor=self.background,
			fg=self.foreground,
			selectforeground=self.foreground,
			selectborderwidth=0,
			justify=justify,
			font=font,
			bd=0
		)

		entry.insert(0, text)
		entry.config(state="readonly", width=len(text))

		return entry

	# creates correctly formatted buttons
	def formatted_buttons(self, frame, text="", bg=None, fg=None,
	justify="left", activebackground=None, command="", activeforeground=None):

		if bg is None:
			bg = self.buttonBackground
		if fg is None:
			fg = self.foreground
		if activebackground is None:
			activebackground = self.buttonActiveBackground
		if activeforeground is None:
			activeforeground = self.foreground

		button = tk.Button(
			frame,
			text=text,
			bg=bg,
			fg=fg,
			justify=justify,
			activebackground=activebackground,
			activeforeground=activeforeground,
			command=command
		)

		return button

	def join_network_window(self):

		def join_network(network):

			try:
				check_output(['zerotier-cli', 'join', network])
				joinResult = "Successfully joined network"
			except:
				joinResult = "Invalid network ID"

			messagebox.showinfo(icon="info", message=joinResult)
			self.refresh_networks()

			joinWindow.destroy()

		joinWindow = self.launch_sub_window("Join Network")

		# widgets
		mainFrame = tk.Frame(joinWindow, padx = 20, pady = 20)

		joinLabel = tk.Label(mainFrame, text="Network ID:")
		networkIdEntry = tk.Entry(mainFrame, font="Monospace")
		joinButton = self.formatted_buttons(mainFrame, text="Join", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: join_network(networkIdEntry.get()))

		# pack widgets
		joinLabel.pack(side="top", anchor="w")
		networkIdEntry.pack(side="top", fill="x")
		joinButton.pack(side="top", fill="x")

		mainFrame.pack(side="top", fill="x")

	def leave_network(self):

		# get selected network
		try:
			self.networkList.curselection()[0]
		except:
			messagebox.showinfo(icon="info", title="Error", message="No network selected")
			return

		network = self.networkList.get('active')
		network = network[:network.find(" ")]

		answer = messagebox.askyesno(title="Leave Network",
			message=f"Are you sure you want to leave {network}?")

		if answer:
			try:
				check_output(['zerotier-cli', 'leave', network])
				leaveResult = "Successfully left network"
			except:
				leaveResult = "Error"
		else:
			return

		messagebox.showinfo(icon="info", message=leaveResult)
		self.refresh_networks()

	def get_status(self):

		status = check_output(['zerotier-cli', 'status']).decode()
		status = status.split()

		# returns a list with status info
		return status

	def about_window(self):

		statusWindow = self.launch_sub_window("About")
		status = self.get_status()

		# frames
		topFrame = tk.Frame(statusWindow, padx=20, pady=30, bg=self.background)
		middleFrame = tk.Frame(statusWindow, padx=20, pady=10, bg=self.background)
		bottomTopFrame = tk.Frame(statusWindow, padx=20, pady=10, bg=self.background)
		bottomFrame = tk.Frame(statusWindow, padx=20, pady=10, bg=self.background)

		# widgets
		titleLabel = tk.Label(topFrame, text="ZeroTier GUI", font=70,
			bg=self.background, fg=self.foreground)

		ztAddrLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("My ZeroTier Address:", status[2])
		)
		versionLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("ZeroTier Version:", status[3]),
			bg=self.background, fg=self.foreground
		)
		ztGuiVersionLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("ZeroTier GUI Version:", "1.2.1"),
			bg=self.background, fg=self.foreground
		)
		statusLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("Status:", status[4]),
			bg=self.background, fg=self.foreground
		)

		closeButton = self.formatted_buttons(bottomTopFrame, text="Close", bg=self.buttonBackground, activebackground=self.buttonActiveBackground,
			command=lambda: statusWindow.destroy()
		)


		# credits
		creditsLabel1 = tk.Label(bottomFrame, text="GUI created by Tomás Ralph",
			bg=self.background, fg=self.foreground)
		creditsLabel2 = self.selectable_text(bottomFrame,
			text="github.com/tralph3/zerotier-gui", justify="center")

		# pack widgets
		titleLabel.pack(side="top", anchor="n")

		ztAddrLabel.pack(side="top", anchor="w")
		versionLabel.pack(side="top", anchor="w")
		ztGuiVersionLabel.pack(side="top", anchor="w")
		statusLabel.pack(side="top", anchor="w")

		closeButton.pack(side="top")

		creditsLabel1.pack(side="top", fill="x")
		creditsLabel2.pack(side="top")

		topFrame.pack(side="top", fill="both")
		middleFrame.pack(side="top", fill="both")
		bottomTopFrame.pack(side="top", fill="both")
		bottomFrame.pack(side="top", fill="both")

		statusWindow.mainloop()

	def get_interface_state(self, interface):

		addressesInfo = check_output(['ip', 'address']).decode()

		stateLine = addressesInfo.find(interface)
		stateStart = addressesInfo.find("state ", stateLine)
		# 6 is the offset for the "state" word
		stateEnd = addressesInfo.find(" ", stateStart + 6)
		state = addressesInfo[stateStart + 6:stateEnd]

		return state

	def toggle_interface_connection(self):

		# setting up
		try:
			idInList = self.networkList.curselection()[0]
		except:
			messagebox.showinfo(icon="info", title="Error", message="No network selected")
			return

		# id in list will always be the same as id in json
		# because the list is generated in the same order
		currentNetworkInfo = self.get_networks_info()[idInList]
		currentNetworkInterface = currentNetworkInfo['portDeviceName']

		state = self.get_interface_state(currentNetworkInterface)

		if state.lower() == "down":
			check_output(['pkexec', 'ip', 'link', 'set', currentNetworkInterface, 'up'])
		else:
			check_output(['pkexec', 'ip', 'link', 'set', currentNetworkInterface, 'down'])

		self.refresh_networks()

	def see_peer_paths(self, peerList):

		# setting up
		try:
			idInList = peerList.curselection()[0]
		except:
			messagebox.showinfo(icon="info", title="Error", message="No peer selected")
			return

		pathsWindow = self.launch_sub_window("Peer Path")

		# frames
		topFrame = tk.Frame(pathsWindow, padx = 20, bg=self.background)
		middleFrame = tk.Frame(pathsWindow, padx = 20, bg=self.background)
		bottomFrame = tk.Frame(pathsWindow, padx = 20, pady = 10, bg=self.background)

		# widgets
		tableLabels = tk.Label(topFrame, font="Monospace",
			bg="grey", fg=self.foreground,
			text="{:9s}{:47s}{:10s}{:16s}{:16s}{:12s}{:17s}".format(
				"Active",
				"Address",
				"Expired",
				"Last Receive",
				"Last Send",
				"Preferred",
				"Trusted Path ID"
			)
		)

		pathsListScrollbar = tk.Scrollbar(middleFrame, bd=2)
		pathsList = tk.Listbox(middleFrame, height="15", font="Monospace",
			selectmode="single", relief="flat", bg="white", fg=self.foreground)

		closeButton = self.formatted_buttons(bottomFrame, text="Close", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: pathsWindow.destroy())
		refreshButton = self.formatted_buttons(bottomFrame, text="Refresh Paths", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: self.refresh_paths(pathsList, idInList))

		# pack widgets
		tableLabels.pack(side="left", fill="both")

		pathsListScrollbar.pack(side="right", fill="both")
		pathsList.pack(side="bottom", fill="x")

		closeButton.pack(side="left", fill="x")
		refreshButton.pack(side="right", fill="x")

		topFrame.pack(side="top", fill="x", pady = (30, 0))
		middleFrame.pack(side="top", fill="x")
		bottomFrame.pack(side="top", fill="x")


		# extra configuration
		self.refresh_paths(pathsList, idInList)

		pathsList.config(yscrollcommand=pathsListScrollbar.set)
		pathsListScrollbar.config(command=pathsList.yview)

		pathsWindow.mainloop()


	def see_peers(self):

		def call_see_peer_paths(event):
			self.see_peer_paths(peersList)

		peersWindow = self.launch_sub_window("Peers")

		# frames
		topFrame = tk.Frame(peersWindow, padx = 20, bg=self.background)
		middleFrame = tk.Frame(peersWindow, padx = 20, bg=self.background)
		bottomFrame = tk.Frame(peersWindow, padx = 20, pady = 10, bg=self.background)

		# widgets
		tableLabels = tk.Label(topFrame, font="Monospace",
			bg="grey", fg=self.foreground,
			text="{:13s}{:13s}{:13s}{:13s}".format(
				"ZT Address",
				"Version",
				"Role",
				"Latency"
			)
		)

		peersListScrollbar = tk.Scrollbar(middleFrame, bd=2)
		peersList = tk.Listbox(middleFrame, width="50", height="15",
			font="Monospace", selectmode="single", relief="flat",
			bg="white", fg=self.foreground
		)

		peersList.bind('<Double-Button-1>', call_see_peer_paths)

		closeButton = self.formatted_buttons(bottomFrame, text="Close", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: peersWindow.destroy()
		)
		refreshButton = self.formatted_buttons(bottomFrame, text="Refresh Peers", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: self.refresh_peers(peersList)
		)
		seePathsButton = self.formatted_buttons(bottomFrame, text="See Paths", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: self.see_peer_paths(peersList)
		)

		# pack widgets
		tableLabels.pack(side="left", fill="both")

		peersListScrollbar.pack(side="right", fill="both")
		peersList.pack(side="bottom", fill="x")

		closeButton.pack(side="left", fill="x")
		refreshButton.pack(side="right", fill="x")
		seePathsButton.pack(side="right", fill="x")

		topFrame.pack(side="top", fill="x", pady = (30, 0))
		middleFrame.pack(side="top", fill="x")
		bottomFrame.pack(side="top", fill="x")


		# extra configuration
		self.refresh_peers(peersList)

		peersList.config(yscrollcommand=peersListScrollbar.set)
		peersListScrollbar.config(command=peersList.yview)

		peersWindow.mainloop()

	def see_network_info(self):

		# setting up
		try:
			idInList = self.networkList.curselection()[0]
		except:
			messagebox.showinfo(icon="info", title="Error", message="No network selected")
			return

		infoWindow = self.launch_sub_window("Network Info")

		# id in list will always be the same as id in json
		# because the list is generated in the same order
		currentNetworkInfo = self.get_networks_info()[idInList]

		# frames
		topFrame = tk.Frame(infoWindow, pady=30, bg=self.background)
		middleFrame = tk.Frame(infoWindow, padx=20, bg=self.background)

		allowDefaultFrame = tk.Frame(infoWindow, padx=20, bg=self.background)
		allowGlobalFrame = tk.Frame(infoWindow, padx=20, bg=self.background)
		allowManagedFrame = tk.Frame(infoWindow, padx=20, bg=self.background)

		bottomFrame = tk.Frame(infoWindow, pady=10, bg=self.background)

		# check variables
		allowDefault = tk.BooleanVar()
		allowGlobal = tk.BooleanVar()
		allowManaged = tk.BooleanVar()

		allowDefault.set(currentNetworkInfo['allowDefault'])
		allowGlobal.set(currentNetworkInfo['allowGlobal'])
		allowManaged.set(currentNetworkInfo['allowManaged'])

		# assigned addresses widget generation
		try:

			assignedAddressesWidgets = []

			# first widget
			assignedAddressesWidgets.append(
				self.selectable_text(
					middleFrame,
					"{:25s}{}".format("Assigned Addresses:",
						currentNetworkInfo['assignedAddresses'][0]),
					font="Monospace"
				)
			)

			# subsequent widgets
			for address in currentNetworkInfo['assignedAddresses'][1:]:
				assignedAddressesWidgets.append(
					self.selectable_text(
						middleFrame,
						"{:>42s}".format(address),
						font="Monospace"
					)
				)

		except IndexError:

			assignedAddressesWidgets.append(
				self.selectable_text(middleFrame, "{:25s}{}".format("Assigned Addresses:", "-"), font="Monospace")
			)

		# widgets
		titleLabel = tk.Label(topFrame, text="Network Info", font=70,
			bg=self.background, fg=self.foreground)

		nameLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("Name:", currentNetworkInfo['name']))
		idLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("Network ID:", currentNetworkInfo['id']))
		statusLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("Status:", currentNetworkInfo['status']),
			bg=self.background, fg=self.foreground
		)
		stateLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("State:", self.get_interface_state(currentNetworkInfo['portDeviceName'])),
			bg=self.background, fg=self.foreground
		)
		typeLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("Type:", currentNetworkInfo['type']),
			bg=self.background, fg=self.foreground
		)
		deviceLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("Device:", currentNetworkInfo['portDeviceName']))
		bridgeLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("Bridge:", currentNetworkInfo['bridge']),
			bg=self.background, fg=self.foreground
		)
		macLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("MAC Address:", currentNetworkInfo['mac']))
		mtuLabel = self.selectable_text(middleFrame, font="Monospace",
			text="{:25s}{}".format("MTU:", currentNetworkInfo['mtu']))
		dhcpLabel = tk.Label(middleFrame, font="Monospace",
			text="{:25s}{}".format("DHCP:", currentNetworkInfo['dhcp']),
			bg=self.background, fg=self.foreground
		)

		allowDefaultLabel = tk.Label(allowDefaultFrame, font="Monospace",
			text="{:24s}".format("Allow Default Route"),
			bg=self.background, fg=self.foreground
		)
		allowDefaultCheck = tk.Checkbutton(allowDefaultFrame, variable=allowDefault,
			command=lambda: change_config("allowDefault", allowDefault.get()),
			bg=self.background, fg=self.foreground
		)

		allowGlobalLabel = tk.Label(allowGlobalFrame, font="Monospace",
			text="{:24s}".format("Allow Global IP"),
			bg=self.background, fg=self.foreground
		)
		allowGlobalCheck = tk.Checkbutton(allowGlobalFrame, variable=allowGlobal,
			command=lambda: change_config("allowGlobal", allowGlobal.get()),
			bg=self.background, fg=self.foreground
		)

		allowManagedLabel = tk.Label(allowManagedFrame, font="Monospace",
			text="{:24s}".format("Allow Managed IP"),
			bg=self.background, fg=self.foreground
		)
		allowManagedCheck = tk.Checkbutton(allowManagedFrame, variable=allowManaged,
			command=lambda: change_config("allowManaged", allowManaged.get()),
			bg=self.background, fg=self.foreground
		)

		closeButton = self.formatted_buttons(bottomFrame, text="Close", bg=self.buttonBackground,
			activebackground=self.buttonActiveBackground, command=lambda: infoWindow.destroy())

		# pack widgets
		titleLabel.pack(side="top", anchor="n")

		nameLabel.pack(side="top", anchor="w")
		idLabel.pack(side="top", anchor="w")

			# assigned addresses
		for widget in assignedAddressesWidgets:
			widget.pack(side="top", anchor="w")

		statusLabel.pack(side="top", anchor="w")
		stateLabel.pack(side="top", anchor="w")
		typeLabel.pack(side="top", anchor="w")
		deviceLabel.pack(side="top", anchor="w")
		bridgeLabel.pack(side="top", anchor="w")
		macLabel.pack(side="top", anchor="w")
		mtuLabel.pack(side="top", anchor="w")
		dhcpLabel.pack(side="top", anchor="w")

		allowDefaultLabel.pack(side="left", anchor="w")
		allowDefaultCheck.pack(side="left", anchor="w")

		allowGlobalLabel.pack(side="left", anchor="w")
		allowGlobalCheck.pack(side="left", anchor="w")

		allowManagedLabel.pack(side="left", anchor="w")
		allowManagedCheck.pack(side="left", anchor="w")

		closeButton.pack(side="top")

		topFrame.pack(side="top", fill="both")
		middleFrame.pack(side="top", fill="both")

		allowDefaultFrame.pack(side="top", fill="both")
		allowGlobalFrame.pack(side="top", fill="both")
		allowManagedFrame.pack(side="top", fill="both")

		bottomFrame.pack(side="top", fill="both")

		# checkbutton functions
		def change_config(config, value):

			# zerotier-cli only accepts int values
			value = int(value)

			try:

				check_output(['zerotier-cli', 'set', currentNetworkInfo['id'], f"{config}={value}"],
					stderr=STDOUT)

			except CalledProcessError as error:

				error = error.output.decode().strip()

				messagebox.showinfo(
					title="Error",
					message=f"Error: \"{error}\"",
					icon="error"
				)

		# needed to stop local variables from being destroyed before the window
		infoWindow.mainloop()

if __name__ == "__main__":

	# automates the process of copying the auth token
	def auth_token_setup():
		if getuid() != 0:

			# get username
			username = check_output(['whoami']).decode()
			username = username.replace("\n", "")

			question = messagebox.askyesno(
				icon="info",
				title="Root access needed",
				message=f"In order to grant {username} access "\
						"to ZeroTier we need temporary root access to "\
						"store the Auth Token in your home folder. "\
						"Otherwise, you would need to run this "\
						"program as root. Grant access?"
			)

			if question:

				# copy auth token to home directory and make the user own it
				system(	f'pkexec bash -c "cp /var/lib/zerotier-one/authtoken.secret '\
						f'/home/{username}/.zeroTierOneAuthToken && chown {username} '\
						f'/home/{username}/.zeroTierOneAuthToken && chmod 0600 '\
						f'/home/{username}/.zeroTierOneAuthToken"'
						)

			else:
				_exit(0)

	# temporary window for popups
	tmp = tk.Tk()
	tmp.withdraw()

	# simple check for zerotier
	try:
		check_output(['zerotier-cli', 'listnetworks'], stderr=STDOUT)

	# in case the command throws an error
	except CalledProcessError as error:

		output = error.output.decode()

		if "missing authentication token" in output:
			messagebox.showinfo(title="Error",
				message="This user doesn't have access to ZeroTier!", icon="error")
			auth_token_setup()
		elif "Error connecting" in output:
			messagebox.showinfo(title="Error",
				message='"zerotier-one" service isn\'t running!', icon="error")
			_exit(1)

	# in case there's no command
	except FileNotFoundError:
		messagebox.showinfo(title="Error",
			message="ZeroTier isn't installed!", icon="error")
		_exit(1)

	# destroy temporary window
	tmp.destroy()

	# create mainwindow class and execute the mainloop
	mainWindow = MainWindow().window
	mainWindow.mainloop()
