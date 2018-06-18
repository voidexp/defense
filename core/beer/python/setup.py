from setuptools import setup


setup(
    name='beer',
    version='0.0.1',
    author='Ivan Nikolaev',
    author_email='voidexp@gmail.com',
    description='Tiny game engine',
    license='BSD',
    keywords='game graphics multimedia',
    packages=['beer'],
    setup_requires=['cffi>=1.0.0'],
    install_requires=['cffi>=1.0.0'],
    package_data={
        'beer': ['../_beer.so'],
    },
    include_package_data=True
)
