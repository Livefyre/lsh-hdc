import re
from functools import partial
from setuptools import setup, find_packages
from pkg_resources import resource_string

requirements = resource_string(
    __name__, 'requirements.txt').splitlines()
dev_requirements = resource_string(
    __name__, 'dev_requirements.txt').splitlines()

<<<<<<< HEAD
# match -f, -e, and so on
match_prefix = partial(re.match, re.compile('^\s*-[a-z]\s+'))

dependency_links = filter(match_prefix, requirements)
install_requires = filter(lambda r: not match_prefix(r), requirements)
tests_require = filter(lambda r: not match_prefix(r), dev_requirements)
=======
# regex for finding URLs in strings
GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
contains_url = partial(re.findall, GRUBER_URLINTEXT_PAT)

dependency_links = filter(contains_url, requirements)
install_requires = filter(lambda r: not contains_url(r), requirements)
tests_require = filter(lambda r: not contains_url(r), dev_requirements)
>>>>>>> 6d6e0de21b2eee7c2c34d326ff063ec4bc36ad31


setup(
    name="lsh-hdc",
    version="0.0.19",
    author="Eugene Scherba",
    author_email="escherba@livefyre.com",
    description=("Algorithms for locality-sensitive hashing on text data"),
    url='https://github.com/Livefyre/lfpylib/tree/lsh/lsh',
    packages=find_packages(exclude=['tests', 'scripts']),
    long_description="LSH algo that uses MinHash signatures",
    install_requires=install_requires,
    dependency_links=dependency_links,
    tests_require=tests_require,
    test_suite='nose.collector',
    classifiers=[
    ],
)
