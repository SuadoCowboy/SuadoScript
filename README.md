# SCCPRebuild
Recreating SCCP(again) using my gdscript version

Created by Suado Cowboy

This project is inspired in the console of
Team Fortress 2, A game made by Valve Corp.

The "plugins" folder is for python scripts that
can be executed inside the console, but to execute
the user needs to load manually.

The "cfg" folder is where the user can put .cfg file
extension type that can be used in the program.

'@' at start of line means that the result of the
function will come back but only if that is defined,
here is an example: incrementvar creates 2 commands:
<incrementvar_name> and @<incrementvar_name>,
@<incrementvar_name> calls incrementvar.get and return
the integer of the incrementvar.
