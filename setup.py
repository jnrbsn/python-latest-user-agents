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
    classifiers=[],
    py_modules=['latest_user_agents'],
    install_requires=[
        'appdirs',
        'requests',
    ],
)
