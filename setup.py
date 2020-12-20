from setuptools import setup

setup(
    name='latest-user-agents',
    version='0.0.1',
    description='Get the latest user agent strings for major browsers and OSs',
    long_description='',
    url='https://github.com/jnrbsn/python-latest-user-agent',
    author='Jonathan Robson',
    author_email='jnrbsn@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
    ],
    py_modules=['latest_user_agents'],
    python_requires='>=3.6',
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
