Todopy2
=======

Todopy2 is tiny Python program that helps you manage your stupid and utterly
simple todo list, that you hold in plain text file (`$HOME/todo.log` by
default).

You might ask yourself: "Why the hell would you keep your todo list in a file?"
If you do, then please move along, there is nothing interesing for you to see
here. This is for the people who need to keep it in the text file, to parse it
with other software, sync it with custom wiki, or Android application, and what
not.

Installation
------------

The easiest way is to install it with pip:

    pip install todopy2

After that, you'll have `todo` executable in your path to invoke.

Usage
-----

**Listing tasks**

To list all task, just invoke the program without any arguments:

    todo

You can use built-in help to refine it a little bit. Consult:

    todo -h

**Adding tasks**

    todo add today 'Shuffle keys to make Dvorak keyboard'

**Starting tasks**

    todo start 1

That number up there is the item number. You can see item numbers when you list
tasks.

**Reseting tasks**

Since you know you will mark stuff as started, and then forget about it:

    todo reset 1

**Marking it as done**

    todo done 1

**Cleaning**

It is just a text file, but we sure do a lot of stuff. This command removes
items that are done:

    todo clean

**Moving around**

You figured out you won't be able to make it today, lets move it to later:

    todo move 1 later

**Removing items**

Yeah, let's not do that at all:

    todo remove 1

License
-------

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
