from setuptools import setup, find_packages

def get_reqs():
    with open('requirements.txt') as reqs:
        for req in reqs.readlines():
            yield req.strip()

setup(
    name='psgroupme',
    version='0.1',
    author='Giulio Frasca',
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_reqs(),
    test_suite='tests',
)
