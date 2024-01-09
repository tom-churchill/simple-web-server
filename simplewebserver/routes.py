from sanic import Blueprint
from sanic import response, exceptions
import os
import bcrypt
import types
from datetime import datetime
from sanic_auth import User
from util import conditional_decorator, get_path_parts, format_bytes
from core import (
    auth,
    env,
    use_login_hash,
    supported_media_extensions,
    sharable_salt,
    sharable_secret_key,
    guid,
    login_hashes
)

bp = Blueprint('routes')


@bp.route('/play-media/<path:path>')
@conditional_decorator(auth.login_required, use_login_hash)
def play_media(_, path=''):
    template = env.get_template('play_media.html')
    html_content = template.render(path=path)
    return response.html(html_content)


@bp.route('/view-text/<path:path>')
@conditional_decorator(auth.login_required, use_login_hash)
def view_text(_, path=''):
    current_directory = os.path.realpath('.')
    full_path = os.path.realpath(os.path.join(current_directory, path))
    if os.path.commonprefix([full_path, current_directory]) != current_directory:
        raise exceptions.Forbidden("Can only serve files from within the current directory")

    path_parts = get_path_parts(path)

    template = env.get_template('view_text.html')

    contents = None
    error = None

    try:
        contents = open(full_path, encoding="utf8", errors="replace").read()
    except IOError:
        error = "Could not read file."
    html_content = template.render(path_parts=path_parts, contents=contents, error=error)
    return response.html(html_content)

def get_file_size(path):
    try:
        return os.path.getsize(path)
    except IOError:
        return None


def get_display_file_size(file_size):
    if file_size is None:
        return ''

    return format_bytes(file_size)


def get_display_file_size_search(file_size):
    if file_size is None:
        return ''

    return str(file_size)

def list_directory(path, display_path, is_logged_in):
    if display_path == '':
        display_path = '.'

    error_message = None

    try:
        directory_contents = os.listdir(path)
    except IOError:
        directory_contents = []
        error_message = "Could not open directory"
    directory_contents.sort(key=lambda a: a.lower())

    file_parts = []
    for name in directory_contents:
        full_path = os.path.join(path, name)
        rel_path = os.path.relpath(full_path, '.')
        name_path = os.path.join(display_path, name)

        is_directory = False
        is_directory_order = 0
        if os.path.isdir(full_path) is True:
            is_directory = True
            is_directory_order = 1

        try:
            date_modified_unix_time = os.path.getmtime(full_path)
            date_modified_iso = datetime.utcfromtimestamp(date_modified_unix_time).strftime('%Y-%m-%d %H:%M:%S')
            date_modified_str = datetime.utcfromtimestamp(date_modified_unix_time).strftime('%d %b %Y %I:%M:%S %p')
        except IOError:
            date_modified_unix_time = 'Unknown'
            date_modified_iso = 'Unknown'
            date_modified_str = 'Unknown'

        file_size = get_file_size(full_path)
        file_size_str = get_display_file_size(file_size)
        file_size_search_str = get_display_file_size_search(file_size)

        # used to know whether to show the play media icon
        is_media = False
        if is_directory is False:
            _, extension = os.path.splitext(full_path)
            if extension.lower() in supported_media_extensions:
                is_media = True

        # creates a shareable link that doesn't require authentication to access
        sharable_link = None
        if is_logged_in is True:
            from itsdangerous import URLSafeTimedSerializer

            salt = sharable_salt
            secret_key = sharable_secret_key

            serializer = URLSafeTimedSerializer(secret_key, salt=salt)
            encrypted_path = serializer.dumps(rel_path)
            sharable_link = '/sharable/{encrypted_path}'.format(encrypted_path=encrypted_path)

        file_parts.append([
            name,
            name_path,
            is_directory,
            is_directory_order,
            date_modified_unix_time,
            date_modified_iso,
            date_modified_str,
            file_size_str,
            file_size_search_str,
            file_size_search_str,
            is_media,
            sharable_link
        ])

    path_parts = get_path_parts(display_path, is_path_directory=True)

    template = env.get_template('path.html')
    html_content = template.render(
        error_message=error_message,
        path_parts=path_parts,
        display_path=display_path,
        file_parts=file_parts,
        is_logged_in=is_logged_in,
        guid=guid
    )
    return html_content


async def handle_path(request, path):
    # make sure we aren't serving up paths from outside of the current directory
    # eg prevents curl 'http://127.0.0.1:8000/%2e%2e/' serving up the parent directory
    current_directory = os.path.realpath('.')
    full_path = os.path.realpath(os.path.join(current_directory, path))
    if os.path.commonprefix([full_path, current_directory]) != current_directory:
        raise exceptions.Forbidden("Can only serve files from within the current directory")

    if os.path.exists(full_path) is False:
        raise exceptions.NotFound("Path does not exist")

    current_user = auth.current_user(request)
    is_logged_in = (current_user is not None)

    if os.path.isdir(full_path) is True:
        # serve an html representation of the directory
        html = list_directory(full_path, path, is_logged_in)

        # prevent any sort of browser caching
        headers = {
            'Cache-Control': 'private, max-age=0, no-cache, no-store',
        }

        return response.html(html, headers=headers)
    else:
        chunk_size = 2 * (1024 ** 2)  # 2mb
        file_size = os.path.getsize(full_path)

        range_object = None
        range_header = request.headers.get('Range')
        if range_header is not None:
            range_object = types.SimpleNamespace()
            range_object.start = 0
            range_object.total = file_size
            range_object.end = range_object.total - 1

            range_ = range_header.split('=')[1]
            requested_start, requested_end = range_.split('-')

            if requested_start != '':
                range_object.start = int(requested_start)

            if requested_end != '':
                range_object.end = int(requested_end)

            range_object.end = min(range_object.end, range_object.start + chunk_size - 1)
            range_object.size = range_object.end - range_object.start + 1

        headers = {'Accept-Ranges': 'Accept-Ranges: bytes'}

        return await response.file_stream(
            full_path,
            headers=headers,
            chunk_size=chunk_size,
            _range=range_object,
        )

@bp.route('/')
async def redirect_example(_request):
    return response.redirect('/path/')


@bp.route('/path/<path:path>')
@conditional_decorator(auth.login_required, use_login_hash)
async def path(request, path=''):
    return await handle_path(request, path)


@bp.route('/sharable/<encrypted_path:path>')
async def sharable(request, encrypted_path=''):
    from itsdangerous import URLSafeTimedSerializer, BadSignature

    salt = sharable_salt
    secret_key = sharable_secret_key

    serializer = URLSafeTimedSerializer(secret_key, salt=salt)
    try:
        path = serializer.loads(encrypted_path)
        return await handle_path(request, path)
    except BadSignature:
        from sanic.exceptions import abort
        abort(404)


@bp.route('/login', methods=['GET', 'POST'])
async def login(request):
    error_message = ""
    if request.method == 'POST':
        password = request.form.get('password', '').encode('utf8')
        for login_hash in login_hashes:
            if bcrypt.checkpw(password, login_hash):
                user = User(id=1, name="name")  # values dont matter
                auth.login_user(request, user)
                return response.redirect('/')
            else:
                error_message = "Incorrect password"

    template = env.get_template('login.html')
    html_content = template.render(error_message=error_message)
    return response.html(html_content)


@bp.route('/logout')
@conditional_decorator(auth.login_required, use_login_hash)
async def logout(request):
    auth.logout_user(request)
    return response.redirect('/')
