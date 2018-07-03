from setuptools import setup, find_packages


MY_VERSION= '1.1'
AUTHOR ='Mehul Prajapati'
EMAIL ='mehul.prajapati@mobileinternet.com'
NAME ='my-client'


setup(
    name=NAME,
    packages=find_packages(exclude=('tests',)),
    version=MY_VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    data_files = [('/opt/my-client/conf', ['conf/exabgp.ini', 'conf/radius.conf'])],
    package_data={'': ['dictionary', 'dictionary.3gpp']},
    include_package_data=True,
    classifiers=[
    'Development Status :: 1',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3.4',
    'Natural Language :: English',
    ],
)

