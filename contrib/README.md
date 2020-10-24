# Extras

This directory contains extra integrations that are running upstream
that you might like to have. These are written specifically for the old
sr.ht upstream instance and if you want to use them, you may have to
edit them.

* [authserver.py](authserver.py) lets you authenticate legacy.sr.ht
accounts over SMTP to use legacy.sr.ht accounts with other things (like 
[gogs](http://gogs.io/docs/features/authentication.html))

## Setup

You have to have legacy.sr.ht available as a module for these to work:

    [sudo] python setup.py install
