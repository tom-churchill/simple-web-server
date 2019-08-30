# Simple Web Server
Simple Web Server is an alternative to pythons http.server and SimpleHTTPServer. It supports multiple connections, authentication and SSL.
![image](https://i.imgur.com/UqeWbKx.png)
## Requirements
Python 3.6+.

## Installation
```
pip install git+https://github.com/tom-churchill/simple-web-server.git
```
## Arguments
```
Usage:
    simplewebserver [options]
    simplewebserver -h | --help

Options:
    -p --port PORT                   Specify alternate port [default: 8000]
    -b --bind ADDRESS                Specify alternate bind address [default: 0.0.0.0]
    -h --help                        Show this help message and exit.

Authentication Options:
    -g --generate-login-hash
        Generate a hash to be used for authentication
    -u --use-login-hash LOGINHASH
        Password protection using the provided hash for authentication
    -a --allow-insecure
        Allows authentication without SSL. Do not use without being fully aware of the security implications!

SSL Options:
    -cf --certificate-file CERTIFICATE_FILE_PATH
        Path to your SSL certificate file
    -ck --certificate-key CERTIFICATE_KEY_PATH
        Path to your SSL certificate key
```
## Examples
At its simplest:
```
python -m simplewebserver
```
Will bind to 0.0.0.0 (all IPs on local machine) with port 8000.

##### Binding to localhost with a custom port
```
python -m simplewebserver --bind 127.0.0.1 --port 8080
```

##### With authentication

First create a login hash (salted bcrypt):
```
python -m simplewebserver --generate-login-hash
Password: **********

Login hash: <generated hash>
```
Then pass the hash in as an argument:
```
python -m simplewebserver --use-login-hash "<generated hash>"
```
It's a good idea to use SSL in case the network between the two computers is compromised.

##### With authentication and encryption
You will need to generate and install a self signed localhost certificate. There are some instructions [here](/CERTIFICATEINSTRUCTIONS.md).
```
python -m simplewebserver --certificate-file "<path to cert.crt>" --certificate-key "<path to cert.key>" --use-login-hash "<generated hash>"
``` 