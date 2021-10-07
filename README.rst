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


Configuration
=============

There are currently 2 ways to configure `jenviz`.

1) adding the Jenkins `url`, `username` and `password` via command line parameters::

     $ jenviz --jenkins-url https://my-jenkins-instance/ --jenkins-user joe --jenkins-password 123 SomeJobName

2) using a `.ini` style configuration file and profiles::

     $ cat ~/.config/jenviz.ini 
     [profile1]
     url=https://my-jenkins-instance
     user=joe
     password=123

     $ jenviz -p profile1 SomeJobName

Contributions
=============

Please use github (https://github.com/toabctl/jenviz) issues
and pull requests for discussions and contribution.

FAQ
===

Why are subprojects are not visible in the output?
++++++++++++++++++++++++++++++++++++++++++++++++++

Try to update the Parameterized Trigger Plugin on the jenkins instance.
