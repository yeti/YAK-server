Contributing
============

YAK-server is an open-source project and we welcome suggestions, questions, and code.

Report bugs, issues, and feature requests to the `Github issue tracker <https://github.com/yeti/yak-server/issues>`_.

Recommended Setup
-----------------

#. Fork and clone your own copy of the `Github repo <https://github.com/yeti/yak-server>`_
#. Create a new python virtual environment
#. ``pip install django djangorestframework``
#. ``pip install -r requirements/requirements-test.txt``

Run Tests
---------

To run the tests, run ``python manage.py test``.

Submitting Changes
------------------

* Open a pull request from your Github repo to ``/yeti/yak-server/master``
    * Provide an overview of your changes
    * Specify any issues (by number) that your PR addresses
* PRs won't be merged if they break tests
* Feel free to ask for help or guidance!

Contributing to the documentation
---------------------------------

The documentation for yak-server is in plain text files and can be viewed using
any text file viewer.

It uses ReST (reStructuredText) [1], and the Sphinx documentation system [2].
This allows it to be built into other forms for easier viewing and browsing.

To create an HTML version of the docs:

* Install Sphinx (using ``pip install Sphinx`` or some other method)

* In this docs/ directory, type ``make html`` (or ``make.bat html`` on
  Windows) at a shell prompt.

The documentation in _build/html/index.html can then be viewed in a web browser.

[1] http://docutils.sourceforge.net/rst.html
[2] http://sphinx-doc.org/
