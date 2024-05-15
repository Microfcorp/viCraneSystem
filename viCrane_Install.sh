#!/bin/bash

PHOTOSCRIPT="/usr/scripts/gopro-photo"

echo -e "\033[33m Start viCrane Installer \033[37m"
echo -e "\033[33m Start not sudo!!!!!!! \033[37m"

sudo mkdir -p "/usr/scripts/"

function APT(){
	echo "Installing service packages..."
	sudo apt install mc
	sudo apt install git
	sudo apt install samba
	echo "Installing python packages..."
	sudo apt install python3
	sudo apt install pip
	echo "Installing network packages..."
	sudo apt install network-manager
	sudo apt install network-manager-config-connectivity-debian
	echo "Installing locale packages..."
	sudo apt install locales
	sudo apt install locales-all
	echo
	echo -e "\033[32m OK \033[30m"
}

function CurrentLocale(){
	echo
	echo -e "\033[36m Current locale: \033[37m"
	sudo localectl status
	echo
}
function SetLocale(){
	echo -e "\033[33m Set location... \033[37m"
	localectl set-locale LANG=en_US.UTF-8
	localectl set-locale LANGUAGE=en_US.UTF-8
	localectl set-locale LC_ALL=en_US.UTF-8
	localectl set-locale LC_CTYPE=en_US.UTF-8
	sudo localectl set-locale LANG=en_US.UTF-8
	sudo localectl set-locale LANGUAGE=en_US.UTF-8
	sudo localectl set-locale LC_ALL=en_US.UTF-8
	sudo localectl set-locale LC_CTYPE=en_US.UTF-8
	#sudo dpkg-reconfigure locales
}
function ConfigureSamba(){
	sudo cp -p -f ./smb.conf /etc/samba/smb.conf
	sudo systemctl enable smbd
	sudo echo -e "junger\njunger" | sudo smbpasswd -a -s root
	sudo systemctl start smbd
    sudo systemctl start nmbd
}
function OpenGOPROInstall(){
	pip install open-gopro
	sudo pip install open-gopro
	pip install pydrive
	sudo pip install pydrive
	sudo pip install oauth2client
	pip install oauth2client
	sudo pip install --force-reinstall PySocks
	pip install --force-reinstall PySocks

	sudo cp -af ./open_gopro /usr/local/lib/python3.9/dist-packages/
	sudo cp -af ./open_gopro ~/.local/lib/python3.9/site-packages/
	
	sudo cp ./gopro-photo $PHOTOSCRIPT
	sudo cp ./client_secrets.json /usr/local/lib/python3.9/dist-packages/open_gopro/demos/client_secrets.json
	sudo cp ./client_secrets.json ~/.local/lib/python3.9/site-packages/open_gopro/demos/client_secrets.json
}
function SearchGOPRO(){
    #/home/admin/.local/lib/python3.9/site-packages/open_gopro/demos/photo.py
	sudo python3 ./pyscripts/searchCameras.py
}
function DisconnectWIFI(){
	sudo ip link set dev wlan0 down
}
function CheckConnectGOPRO(){
	sudo python3 ./pyscripts/checkCameras.py --identifier $GOPROID
}
function CheckPhoto(){
	sudo python3 $PHOTOSCRIPT --identifier $GOPROID
}
function InstallCrontab(){
	#* *    * * *   root     cd /home/admin/ && python /home/admin/gopro-photo --identifier 7807
	sudo sed -i "/gopro-photo/d" /etc/crontab
	echo "* *    * * *   root     cd /mnt/ && python3 $PHOTOSCRIPT --identifier $GOPROID" | sudo tee -a /etc/crontab > /dev/null
}

sudo cp ./gopro-photo $PHOTOSCRIPT
APT
CurrentLocale
SetLocale
CurrentLocale
ConfigureSamba
OpenGOPROInstall
DisconnectWIFI
SearchGOPRO
read -e -p "Enter gopro ID (xxxx): " GOPROID #7807
CheckConnectGOPRO
DisconnectWIFI
CheckPhoto
InstallCrontab