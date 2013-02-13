#!/usr/bin/python2
# 'To be done' file parser
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

# todo.py start 5 - done
# todo.py reset 5 - done
# todo.py done 5 - done
# todo.py add today 'Something' - done
# todo.py clean - done
# todo.py move 5 today -done
# todo.py remove 5 - done
# todo.py -a - done
# todo.py -t - done
# todo.py -s - done
# todo.py -l - done

# TODO:
#
# python package
# git repo
# error handling
# custom todo file
# program configuration file ~/.todopyrc
# help
# better parameters handling (use todo.py ls, and argparse)


from optparse import OptionParser


class TodoParser:
    """ To-do file manipulation class.

    Creates and updates to-do file.

    :param filename: The name of the to-do file.
    :type filename: string
    :param options: Parsed program options.
    :type options: dict
    """

    def __init__(self, filename, options):
        self.item_mark = 1
        self.changed = False
        self.opt_all = options.opt_all
        self.filename = filename
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
        self.todo = self.parse_todo(filename)

    def __del__(self):
        if self.changed:
            contents = ''
            modes=['today', 'soon', 'later']
            for mode in modes:
                contents += self.txt[mode]
                mode_items = self.todo.get(mode, [])
                for item in mode_items:
                    contents += '['+ item['status'] +'] ' + item['data'] + '\n';
                contents += '\n'
            contents += self.txt['footer']

            file = open(self.filename, 'w')
            file.write(contents)
            file.close()

    def parse_todo(self, filename):
        """
        Parse txt todo file into a variable.
        """
        todo_file = open(filename)
        todo_data = {}
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
            if self.opt_all:
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
                    if self.opt_all or item['status'] != '+':
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


def parse_parameters():
    """
    Parse command line parameters.
    """
    parser = OptionParser()
    parser.add_option("-a", "--all", action="store_true",  dest="opt_all",
                  help="show all tasks")
    parser.add_option("-t", "--today", action="store_const",
                  dest="opt_today", const="today",
                  default=None, help="show today")
    parser.add_option("-s", "--soon", action="store_const",
                  dest="opt_soon", const="soon",
                  default=None, help="show soon")
    parser.add_option("-l", "--later", action="store_const",
                  dest="opt_later", const="later",
                  default=None, help="show later")
    return parser.parse_args()

if __name__ == '__main__':
    (options, args) = parse_parameters()
    todo = TodoParser('/home/kotnik/todo.log', options);

    if len(args) == 0:
        modes = []
        if (not options.opt_today and not options.opt_soon and not options.opt_later):
            modes = ['today', 'soon', 'later']
        if options.opt_today:
            modes.append('today')
        if options.opt_soon:
            modes.append('soon')
        if options.opt_later:
            modes.append('later')
        print todo.current(modes)
    else:
        if args[0] == 'start':
            ret_str = todo.start(int(args[1]))
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
        elif args[0] == 'reset':
            ret_str = todo.reset(int(args[1]))
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
        elif args[0] == 'done':
            ret_str = todo.done(int(args[1]))
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
        elif args[0] == 'remove':
            ret_str = todo.remove(int(args[1]))
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
        elif args[0] == 'add':
            ret_str = todo.add(args[1], args[2])
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
        elif args[0] == 'clean':
            ret_str = todo.clean()
            if len(ret_str) == 0:
                print "Nothing done."
            else:
                print ret_str
        elif args[0] == 'move':
            ret_str = todo.move(int(args[1]), args[2])
            if len(ret_str) == 0:
                print "Nothing to do."
            else:
                print ret_str
