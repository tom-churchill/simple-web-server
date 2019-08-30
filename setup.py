import setuptools
import sys

if sys.version_info.major == 3:
    # noinspection PyArgumentList
    long_description = open('README.md', encoding='utf-8').read()
else:
    # noinspection PyUnresolvedReferences
    long_description = open('README.md').read().decode("utf-8")

setuptools.setup(
    name='simple-web-server',
    version='1.0.0',
    author='Tom Churchill',
    author_email='tom@tomchurchill.co.uk ',
    description='An alternative to http.server which supports multiple connections, authentication and SSL.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/tom-churchill/simple-web-server',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        'sanic>=19.6.3',
        'Sanic-CookieSession>=0.2.0',
        'bcrypt>=3.1.7',
        'Sanic-Auth>=0.2.0',
        'docopt>=0.6.2',
        'Jinja2>=2.10.1',
    ],
    include_package_data=True,
)