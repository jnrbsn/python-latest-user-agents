from setuptools import setup

with open('README.rst', 'r') as f:
    long_description = f.read().split('\n\n-----\n\n', 1)[1].lstrip()

setup(
    name='latest-user-agents',
    version='0.0.4',
    description='Get the latest user agent strings for major browsers and OSs',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/jnrbsn/python-latest-user-agents',
    author='Jonathan Robson',
    author_email='jnrbsn@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
    ],
    py_modules=['latest_user_agents'],
    python_requires='>=3.8',
    install_requires=[
        'appdirs',
        'requests',
    ],
    extras_require={
        'test': [
            'flake8',
            'flake8-bugbear',
            'flake8-isort',
            'freezegun',
            'pep8-naming',
            'pytest',
            'pytest-cov',
            'pytest-mock',
        ],
    },
)
