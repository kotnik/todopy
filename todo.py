#!/usr/bin/env python
#
# To-do file parser
#
# Copyright (C) 2011  Nikola Kotur <kotnick@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# TODO:
#
# Error handling
# Program configuration in ~/.todopyrc

from __future__ import print_function

import sys
import argparse
from os.path import expanduser

class TodoParser:
    """ To-do file manipulation class.

    Creates and updates to-do file.

    :param options: Parsed program options.
    :type options: dict
    """

    def __init__(self, options):
        self.item_mark = 1
        self.changed = False
        self.options = options
        self.txt = {}
        self.txt['today']  = '---------------------------------\n'
        self.txt['today'] += '|          TODO TODAY           |\n'
        self.txt['today'] += '---------------------------------\n'
        self.txt['soon']  = '---------------------------------\n'
        self.txt['soon'] += '|          TODO SOON            |\n'
        self.txt['soon'] += '---------------------------------\n'
        self.txt['later'] = '---------------------------------\n'
        self.txt['later'] += '|          TODO LATER           |\n'
        self.txt['later'] += '---------------------------------\n'
        self.txt['footer'] = '-' * 88
        self.txt['footer'] += '\n\n'
        self.txt['footer'] += 'LEGEND:\n'
        self.txt['footer'] += '[+]This is a task I have already completed\n'
        self.txt['footer'] += '[.]This is a task I have started but not completed\n'
        self.txt['footer'] += '[ ]This is a task I intend to complete today, soon or later\n'
        self.todo = self.parse_todo(options.config)

    # TODO: refactor me: don't use __del__
    def __del__(self):
        self.save_todo()

    def save_todo(self, force=False):
        if force or self.changed:
            contents = ''
            modes=['today', 'soon', 'later']
            for mode in modes:
                contents += self.txt[mode]
                try:
                    mode_items = self.todo.get(mode, [])
                    for item in mode_items:
                        contents += '['+ item['status'] +'] ' + item['data'] + '\n';
                    contents += '\n'
                except AttributeError:
                    pass
            contents += self.txt['footer']

            file = open(self.options.config, 'w')
            file.write(contents)
            file.close()

    def parse_todo(self, filename):
        """
        Parse txt todo file into a variable.
        """
        todo_data = {}
        try:
            todo_file = open(filename)
            mode = 'today'
            done_parsing = False
            for line in todo_file:
                if line.strip():
                    if line.startswith('-' * 40):
                        done_parsing = True
                    if done_parsing or line.startswith('--'):
                        continue
                    if line.startswith('|'):
                        if 'TODO TODAY' in line:
                            mode = 'today'
                        elif 'TODO SOON' in line:
                            mode = 'soon'
                        elif 'TODO LATER' in line:
                            mode = 'later'
                        continue
                    if (not mode in todo_data):
                        todo_data[mode] = []

                    todo_item = self.parse_todo_item(line.strip())
                    todo_data[mode].append(todo_item)
        except IOError:
            # There is no file, create it.

            self.save_todo(force=True)
        return todo_data

    def parse_todo_item(self, line):
        todo_item = {}
        item_description = line[4:]
        status = line[1:2]
        todo_item['data'] = item_description
        todo_item['status'] = status
        todo_item['mark'] = self.item_mark
        self.item_mark += 1
        return todo_item

    # not used
    def parse_status(self, status_char):
        return {
            ' ': 'todo',
            '.': 'started',
            '+': 'done',
        }[status_char]

    def current(self, modes=['today', 'soon', 'later']):
        out = ''
        for mode in modes:
            empty_block = True
            if self.options.opt_all:
                empty_block = False
            else:
                mode_items = self.todo.get(mode, [])
                for item in mode_items:
                    if item['status'] != '+':
                        empty_block = False
                        continue
            if not empty_block and mode in self.todo:
                if len(self.todo[mode]):
                    out += '\n' + mode.upper() + '\n-----\n'
                for item in self.todo[mode]:
                    if self.options.opt_all or item['status'] != '+':
                        item_desc = item['data']
                        if item['status'] == '+':
                            item_desc = '(DONE) ' + item_desc
                        elif item['status'] == '.':
                            item_desc = '(ON) ' + item_desc
                        out += "%02d" % (item['mark'],) + ': ' + item_desc
                        out += '\n'
        return out

    def mark_item(self, num, mark, title):
        out = ''
        modes=['today', 'soon', 'later']
        for mode in modes:
            if mode in self.todo:
                for item in self.todo[mode]:
                    if item['mark'] == num and item['status'] != mark:
                        # Update tree
                        self.todo[mode].remove(item)
                        item['status'] = mark
                        self.todo[mode].append(item)
                        self.changed = True
                        out = title + ': ' + item['data']
        return out

    def start(self, num):
        return self.mark_item(num, '.', 'Started')

    def reset(self, num):
        return self.mark_item(num, ' ', 'Reset')

    def done(self, num):
        return self.mark_item(num, '+', 'Done')

    def add(self, when, what):
        if when not in ['today', 'soon', 'later']:
            return "Error: please use today, soon or later for time reference"

        item = {}
        item['data'] = what
        item['status'] = ' '
        self.changed = True
        if not when in self.todo:
            self.todo[when] = []
        self.todo[when].append(item)
        return 'Added: ' + what

    def remove(self, num):
        out = ''
        modes=['today', 'soon', 'later']
        for mode in modes:
            if self.todo[mode]:
                for item in self.todo[mode]:
                    if item['mark'] == num:
                        # Update tree
                        self.todo[mode].remove(item)
                        self.changed = True
                        out = 'Removed: ' + item['data']
        return out

    def clean(self):
        out = ''
        items = []
        modes=['today', 'soon', 'later']
        for mode in modes:
            for item in self.todo.get(mode, []):
                if item['status'] == '+':
                    items.append(item['mark'])
                    out += 'Removed: ' + item['data'] + '\n'
        for item in items:
            self.remove(item)
        return out

    def move(self, what, where):
        out = ''
        modes=['today', 'soon', 'later']
        if not where in modes:
            return 'Wrong place to move.'
        for mode in modes:
            for item in self.todo.get(mode, []):
                if item['mark'] == what:
                    self.todo[mode].remove(item)
                    if not self.todo.get(where, False):
                        self.todo[where] = []
                    self.todo[where].append(item)
                    self.changed = True
                    out = 'Moved: ' + item['data']
        return out


if __name__ == '__main__':
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration file location",
                        default="%s/todo.log" % expanduser("~"))
    subparsers = parser.add_subparsers(
        dest="action", help='commands, use [command -h] to get additional help'
    )

    # Listing to-do items.
    list_parser = subparsers.add_parser("ls", help='list to-do items')
    list_parser.add_argument("-a", "--all", action="store_true",  dest="opt_all",
                  help="show all tasks")
    list_parser.add_argument("-t", "--today", action="store_const",
                  dest="opt_today", const="today",
                  default=None, help="show today")
    list_parser.add_argument("-s", "--soon", action="store_const",
                  dest="opt_soon", const="soon",
                  default=None, help="show soon")
    list_parser.add_argument("-l", "--later", action="store_const",
                  dest="opt_later", const="later",
                  default=None, help="show later")

    # Start to-do item.
    start_parser  = subparsers.add_parser("start", help="start to-do item")
    start_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Reset to-do item.
    reset_parser  = subparsers.add_parser("reset", help="reset to-do item")
    reset_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Mark to-do item as done.
    done_parser  = subparsers.add_parser("done", help="mark to-do item as done")
    done_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Remove to-do item.
    remove_parser  = subparsers.add_parser("remove", help="remove to-do item")
    remove_parser.add_argument("item", action="store", help="number of to-do item", type=int)

    # Clean to-do items.
    clean_parser  = subparsers.add_parser("clean", help="remove all done to-do items")

    # Add to-do item.
    add_parser  = subparsers.add_parser("add", help="add to-do item")
    add_parser.add_argument("when", action="store", help="list to add to, one of: [today | soon | later]")
    add_parser.add_argument("desc", action="store", help="to-do item description, enclose in quotes")

    # Move to-do item.
    move_parser  = subparsers.add_parser("move", help="move to-do item")
    move_parser.add_argument("item", action="store", help="number of to-do item", type=int)
    move_parser.add_argument("where", action="store", help="list to move to, one of: [today | soon | later]")

    options = parser.parse_args()
    if not options.action:
        options.action = "ls"
        options.opt_today = options.opt_soon = options.opt_later = options.opt_all = None

    print (options)
    print (sys.argv)

    todo = TodoParser(options);

    if options.action == "ls":
        modes = []
        if (not options.opt_today and not options.opt_soon and not options.opt_later):
            modes = ['today', 'soon', 'later']
        if options.opt_today:
            modes.append('today')
        if options.opt_soon:
            modes.append('soon')
        if options.opt_later:
            modes.append('later')
        print(todo.current(modes))
    else:
        if options.action == 'start':
            ret_str = todo.start(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'reset':
            ret_str = todo.reset(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'done':
            ret_str = todo.done(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'remove':
            ret_str = todo.remove(options.item)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'add':
            ret_str = todo.add(options.when, options.desc)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
        elif options.action == 'clean':
            ret_str = todo.clean()
            if len(ret_str) == 0:
                print("Nothing done.")
            else:
                print(ret_str)
        elif options.action == 'move':
            ret_str = todo.move(options.item, options.where)
            if len(ret_str) == 0:
                print("Nothing to do.")
            else:
                print(ret_str)
