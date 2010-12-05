
# todo for 0.999999999999996e

## MAJOR:

*   new module : factoids
    > This module will makes available factoids. Those are users made.

### Factoids

Needs to be unique, so a way to check registered commands from other
modules could be helpfull.

The database or file used to store factoids isn't actually choosed. There
are two specific points :

1.  Must be easily editable from the command line or with any text editor.
2.  Can not introduce a too high load time at app start.

The simplest way to implement it would be to use the yaml format and
simple load the file into memory. Aliases are easy to do with PyYaml.

## MINOR:

* (auto) transform long urls into bitly tiny urls

