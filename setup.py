from setuptools import setup, find_packages


VERSION= '0.1'
AUTHOR ='Mehul Prajapati'
EMAIL = 'mehul.prajapati@xxx.xxx'
NAME = 'my-package'


setup(
    name=NAME,
    packages=find_packages(exclude=('tests',)),
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    data_files = [('/etc/pkg', ['conf/c1.ini', 'conf/c2.ini'])],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3.4',
    'Natural Language :: English',
    ],
)
