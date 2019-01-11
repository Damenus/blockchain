from setuptools import setup, find_packages

setup(
    name='blockchain',
    author='Damian Darczuk',
    description='Simple use blockchain technology',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Blokchain',
    ],
    install_requires=[
          'requests==2.20.1',
          'colorlog==3.1.4',
          'logging-tree==1.7',
          'flask==1.0.2',
    ],
    tests_require=[
          'pytest',
          'pytest-cov',
          'flake8'
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
