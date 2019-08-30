## Creating a self signed localhost certificate

Create the file 'csrconfig.txt' replacing alt names with those applicable to your computer


```
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = localhost
[ req_ext ]
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=critical,serverAuth,clientAuth
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = localhost
DNS.1 = my-pc # <- Change this to your computer name
IP.0 = 127.0.0.1
IP.1 = 192.168.1.2 # <- Change this to your LAN IP address
```

Then create the file 'certconfig.txt' replacing alt names with those applicable to your computer
```
[ req ]
default_md = sha256
prompt = no
req_extensions = req_ext
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
commonName = localhost
[ req_ext ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=critical,serverAuth,clientAuth
subjectAltName = @alt_names
[ alt_names ]
DNS.0 = localhost
DNS.1 = my-pc # <- Change this to your computer name
IP.0 = 127.0.0.1
IP.1 = 192.168.1.2 # <- Change this to your LAN IP address
```
Now run the following commands. You will need to have openssl installed.
``` 
openssl genpkey -outform PEM -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out cert.key
openssl req -new -nodes -key cert.key -config csrconfig.txt -out cert.csr
openssl req -x509 -nodes -in cert.csr -days 0 -key cert.key -config certconfig.txt -extensions req_ext -out cert.crt
```
You will now have cert.key and cert.crt which are the required files. You will then need to install cert.crt as a trusted root certificate on any computers you wish to access the server from.   