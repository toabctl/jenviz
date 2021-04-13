jenviz
------

`jenviz` is a command line tool to visualize your Jenkins
job relationships.

Installation
============

Into a `virtualenv`::

  virtualenv venv
  source venv/bin/activate
  pip install -e .
  # now you can use the tool
  jenviz -h

Contributions
=============

Please use github (https://github.com/toabctl/jenviz) issues
and pull requests for discussions and contribution.

FAQ
===

Why are subprojects are not visible in the output?
++++++++++++++++++++++++++++++++++++++++++++++++++

Try to update the Parameterized Trigger Plugin on the jenkins instance.
