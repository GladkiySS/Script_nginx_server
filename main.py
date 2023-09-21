#!/usr/bin/python3
import subprocess
import sys
import os

def main():
    # Checking if the virtual server name is specified
    if len(sys.argv) == 1:
        print("\nYou must specify the name of the virtual server.\n")
        sys.exit(1)

    # Reading the name of the virtual server from the command line
    server_name = sys.argv[1]

    # Installing Nginx (if not installed)
    is_nginx()

    subprocess.run(['sudo', 'systemctl', 'stop', 'nginx'])

    # Creating a directory for storing virtual server files and securing access rights for the user.
    os.makedirs(f'/var/www/{server_name}/html', exist_ok=True)
    subprocess.run(['sudo', 'chown', '-R', f'{os.getlogin()}:{os.getlogin()}', f'/var/www/{server_name}/html'])

    create_conf_file(server_name)

    create_html(server_name)

    # Creating a symbolic link from sites-available to sites-enabled
    subprocess.run(['sudo', 'ln', '-s', f'/etc/nginx/sites-available/{server_name}', '/etc/nginx/sites-enabled/'])

    # To avoid the potential hash bucket memory problem
    subprocess.run(['sudo', 'sed', '-i', 's/# server_names_hash_bucket_size 64;/server_names_hash_bucket_size 64;/', '/etc/nginx/nginx.conf'])

    # Checking for errors in the configuration
    if subprocess.run(['sudo', 'nginx', '-t']).returncode == 0:
        # Restarting Nginx to apply the new configuration
        subprocess.run(['sudo', 'systemctl', 'start', 'nginx'])
        print(f"Virtual server {server_name} successfully configured.")
    else:
        print("Nginx configuration error.")


def is_nginx():
    try:
        subprocess.run(['nginx', '-v'])
    except FileNotFoundError:
        print("\nInstalling Nginx...\n")
        install_nginx()


def install_nginx():
    subprocess.run(['sudo', 'apt', 'update'])
    subprocess.run(['sudo', 'apt', 'install', '-y', 'nginx'])


def create_conf_file(server_name):
    # Creating a configuration file for a virtual server
    print(f"\nCreating a configuration file for the virtual server {server_name}...\n")

    config = f"""
	server {{
    		listen 80;
    		listen [::]:80;

    		server_name {server_name};

    		root /var/www/{server_name}/html;
    		index index.html;

    		location / {{
        	try_files $uri $uri/ =404;
    		}}
	}}
    """

    with open(f'/etc/nginx/sites-available/{server_name}', 'w') as nginx_file:
        nginx_file.write(config)


def create_html(server_name):
    # Creating an html page
    html_file = """
	<html>
  		<body>
     	   		Hello, {server_name}
    		</body>
	</html>
     """.format(server_name)

    with open(f'/var/www/{server_name}/html/index.html', 'w') as index_file:
        index_file.write(html_file)


if __name__ == "__main__":
    main()