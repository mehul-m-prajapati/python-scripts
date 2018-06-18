from setuptools import setup, find_packages


GX_VERSION= '0.1'
AUTHOR ='Mehul Prajapati'
EMAIL = 'mehul.prajapati@mobileinternet.com'
NAME = 'gx-call-handler'


setup(
    name=NAME,
    packages=find_packages(exclude=('tests',)),
    version=GX_VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    data_files = [('/etc/gx', ['conf/exabgp.ini', 'conf/gx_config.ini'])],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3.4',
    'Natural Language :: English',
    ],
)

