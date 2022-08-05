# Requirements
Python 3.x (Python 3.9 is recommended)

# Usage
SuadoScript is meant to be used for games to configure them. Nonetheless
It is not prohibited to use in other types of programs.

# Examples
It can make simple functions: Imagine a 3d game with the function to crouch
and another function to jump, with SuadoScript you could create an alias that crouches and jumps
at the same time.

and also complex functions: Imagine a game with the function of binding a key to multiple commands,
if you want to create something like a menu of binds, you can, all you need is time, thinking and
a little of the game commands knowledge.

# Folders usage
The "plugins" folder is for python scripts that can be executed inside
the interpreter. To execute the user need to load them manually. If you
are looking to load them automatically, you would need to put in the code
a line with the "load_plugin" function to execute it.

The "cfg" folder is where SuadoScript files should be. Nonetheless, it could
be executed from anywhere.

# Understanding the usage of "@"
"@" at the start of a command means that the result of the function will
return, but only if that is defined, here is an example: incrementvar
creates 2 commands: <incrementvar_name> and @<incrementvar_name>,
@<incrementvar_name> calls incrementvar.get and return the value of the
incrementvariable.

# Created with time and love by
Suado Cowboy

# Extra
Altough It is made in python, I intend to make it in gdscript (godot language)
and maybe other languages like java, c++, c# and javascript.
