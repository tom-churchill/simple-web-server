from sanic import Sanic
from sanic import response
import sanic_cookiesession
from getpass import getpass
import os
import bcrypt
import ssl
from .util import generate_random_hash
from .routes import bp
from .core import auth, dir_path, guid, host, port, generate_login_hash, use_login_hash, certificate_file, certificate_key, allow_insecure

# initialise Sanic
app = Sanic(__name__)
app.blueprint(bp)

# initialise Sanic-CookieSession
# using a random hash as the secret key will mean sessions won't persist between process restarts, however the
# alternative would either be adding a command line argument which would be insecure (bcrypt hash is slow enough to
# crack to not be an issue1)
app.config['SESSION_COOKIE_SECRET_KEY'] = generate_random_hash()
app.config['SESSION_COOKIE_SALT'] = generate_random_hash()
app.config['SESSION_COOKIE_NAME'] = '_{guid}_session'.format(guid=guid)

if allow_insecure is True:
    # allows cookies to be set over http instead of just https
    app.config['SESSION_COOKIE_SECURE'] = False

sanic_cookiesession.setup(app)

# initialise Sanic-Auth
app.config.AUTH_LOGIN_ENDPOINT = 'routes.login'
auth = auth.setup(app)


# Sanic for some reason removes the Content-Length header when streaming a response.
# This means that a file downloading won't show its progress.
# This is a workaround to monkey patch the Content-Length header back in.
# When the Hook-Content-Length header is set it will set the Content-Length header
# to its value and then delete itself.
# noinspection PyProtectedMember
old_parse_headers = response.StreamingHTTPResponse._parse_headers


def hooked_parse_headers(self):
    if 'Monkey-Patch-Content-Length' in self.headers is not None:
        self.headers['Content-Length'] = self.headers['Monkey-Patch-Content-Length']
        del self.headers['Monkey-Patch-Content-Length']

    return old_parse_headers(self)


response.StreamingHTTPResponse._parse_headers = hooked_parse_headers


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
        static_directory = os.path.join(dir_path, 'static')
        app.static('/static', static_directory)

        # setup ssl
        context = None
        if certificate_file is not None and certificate_key is not None:
            context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certificate_file, keyfile=certificate_key)

        app.run(host=host, port=port, debug=False, ssl=context)
