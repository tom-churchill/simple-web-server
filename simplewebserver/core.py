import bcrypt
from sanic_auth import Auth
import docopt
import os
import sys
from jinja2 import Environment, FileSystemLoader
from util import generate_random_hash

help_string = """
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
"""


dir_path = os.path.dirname(__file__)
supported_media_extensions = {'.mkv', '.mp4', '.webm', '.ogg', '.aac', '.flac', '.m4a', '.mp3', '.wav'}
guid = "f2f08a5c-6377-4a90-9b92-379621353d05"
auth = Auth()

args = docopt.docopt(help_string)
port = int(args['--port'])
host = args['--bind']
generate_login_hash = args['--generate-login-hash']
use_login_hash = args['--use-login-hash']
allow_insecure = args['--allow-insecure']
certificate_file = args['--certificate-file']
certificate_key = args['--certificate-key']
sharable_salt = generate_random_hash()
sharable_secret_key = generate_random_hash()

login_hashes = []
if use_login_hash is not None:
    # convert the input hashes into a list of bytestring hashes
    login_hashes = [i.replace(":", "$").encode('utf8') for i in use_login_hash.split(',')]

    # check that supplied hashes are valid
    for login_hash in login_hashes:
        try:
            bcrypt.checkpw(b"", login_hash)
        except ValueError:
            raise ValueError("Invalid login hash")

package_directory = os.path.dirname(sys.argv[0])
template_directory = os.path.join(package_directory, 'templates')
env = Environment(loader=FileSystemLoader(template_directory))
