from setuptools import setup, find_packages
from os import path
from pkg_resources import parse_requirements

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, 'r') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


setup(
    name='strarnavi',
    version='0.0.1',
    description='provides API to creates posts and comments',
    long_description=long_description,
    long_description_content_type='text/markdown',
    # git url
    url='',
    include_package_data=True,
    package_data={
        '': ['requirements.txt', 'requirements.dev.txt'],
    },
    data_files=[
        ('', ['requirements.txt', 'requirements.dev.txt']),
    ],
    author='Dima Moroz',
    author_email='d1m.moroz007@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Database :: Front-Ends',
        'License :: Free For Educational Use',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='starnavi api database posts comments',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6',
    install_requires=load_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'run_alembic=starnavi.scripts.run_alembic:main',
        ]
    },
    # https://setuptools.readthedocs.io/en/latest/setuptools.html
    # #declaring-extras-optional-features-with-their-own-dependencies
    extras_require={'dev': load_requirements('requirements.dev.txt')},
    project_urls={}
)
