latest-user-agents
==================

*Get the latest user agent strings for major browsers and OSs*

-----

Installation
------------

To install via pip::

    pip install latest-user-agents

Or download the source code and install manually::

    git clone https://github.com/jnrbsn/python-latest-user-agents.git
    cd python-latest-user-agents/
    python setup.py install

Basic usage
-----------

.. code:: python

    In [1]: from latest_user_agents import get_latest_user_agents, get_random_user_agent

    In [2]: get_latest_user_agents()
    Out[2]:
    ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.6; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.6; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.86',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.2651.86']

    In [3]: get_random_user_agent()
    Out[3]: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

    In [4]: get_random_user_agent()
    Out[4]: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'

    In [5]: get_random_user_agent()
    Out[5]: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'

Bugs, requests, questions, etc.
-------------------------------

Please create an `issue on GitHub <https://github.com/jnrbsn/python-latest-user-agents/issues>`_.
