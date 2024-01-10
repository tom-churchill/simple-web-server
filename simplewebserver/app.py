import os
import sanic_cookiesession
from sanic import Sanic
from simplewebserver.core import auth, dir_path, guid, allow_insecure
from simplewebserver.routes import bp
from simplewebserver.util import generate_random_hash


def create_app():
    # initialise Sanic
    app = Sanic("simplehttpserver")

    static_directory = os.path.join(dir_path, 'static')
    app.static('/static', static_directory)

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
    auth.setup(app)

    return app
