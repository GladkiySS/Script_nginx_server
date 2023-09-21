#!/bin/bash

# Checking if the virtual server name is specified
if [ $# -eq 0 ]; then
    echo -e "\nYou must specify the name of the virtual server.\n"
    exit 1
fi

# Reading the name of the virtual server from the command line
server_name="$1"

# Installing Nginx (if not installed)
if ! command -v nginx > /dev/null; then
    echo -e "\nInstalling Nginx...\n"
    sudo apt-get update
    sudo apt-get install -y nginx
fi

sudo systemctl stop nginx

# Creating a configuration file for a virtual server
echo -e "\nCreating a configuration file for the virtual server $server_name...\n"

config="
server {
	listen 80;
	listen [::]:80;

	server_name $server_name;

	root /var/www/$server_name/html;
	index index.html;

	location / {
		try_files \$uri \$uri/ =404;
	}
}
"

echo "$config" | sudo tee /etc/nginx/sites-available/$server_name > /dev/null

# Creating a directory for storing virtual server files and securing access rights for the user.
sudo mkdir -p /var/www/$server_name/html
sudo chown -R $USER:$USER /var/www/amigalocal.com/html

# Creating an html page
html_file="
<html>
	<body>
		Hello, $server_name
	</body>
</html>
"

echo "$html_file" | sudo tee /var/www/$server_name/html/index.html > /dev/null

# Creating a symbolic link from sites-available to sites-enabled
sudo ln -s /etc/nginx/sites-available/$server_name /etc/nginx/sites-enabled/

# To avoid the potential hash bucket memory problem
sudo sed -i "s/# server_names_hash_bucket_size 64;/server_names_hash_bucket_size 64;/" /etc/nginx/nginx.conf

# Checking for errors in the configuration
if sudo nginx -t; then
    # Restarting Nginx to apply the new configuration
    sudo systemctl start nginx
    echo -e "Virtual server $server_name successfully configured.\n"
else
    echo -e "Nginx configuration error.\n"
fi
