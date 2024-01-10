from sanic import Sanic
from sanic.worker.loader import AppLoader
from getpass import getpass
import os
import bcrypt
import ssl
from simplewebserver.app import create_app
from simplewebserver.core import host, port, generate_login_hash, use_login_hash, certificate_file, certificate_key, allow_insecure


def generate_login_hash_function():
    password = getpass("Password: ").strip().encode('utf8')

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt).decode('utf8')
    # shells use $ as an escape character, so replace it with a different character
    hashed = hashed.replace("$", ":")

    print((
        '\n'
        'Login hash: {hashed}\n'
        '\n'
        'Example Usage: \n'
        'python -m simplewebserver --use-login-hash "{hashed}" \n'
        '\n'
        'Then login through your internet browser using the password inputted when generating the hash.'
    ).format(hashed=hashed))


if __name__ == '__main__':
    if generate_login_hash is True:
        generate_login_hash_function()
    elif use_login_hash is not None and allow_insecure is False and (certificate_file is None or certificate_key is None):
        print("Authentication without SSL is only possible if the --allow-insecure flag is set.")
        print("Only use if you are aware of the security implications.")
    else:
        os.environ['SANIC_IGNORE_PRODUCTION_WARNING'] = 'true'

        # setup ssl
        ssl = None
        if certificate_file is not None and certificate_key is not None:
            ssl = dict(cert=certificate_file, key=certificate_key)

        loader = AppLoader(factory=create_app)
        app = loader.load()
        app.prepare(host=host, port=port, dev=False, debug=False, ssl=ssl)
        Sanic.serve(primary=app, app_loader=loader)
