#!/usr/bin/python
# -*- coding: utf-8 -*-

# new_config.py file is part of slpkg.

# Copyright 2014-2017 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import os
import shutil
import itertools

from slpkg.messages import Msg
from slpkg.utils import Utils
from slpkg.__metadata__ import MetaData as _meta_


class NewConfig(object):
    """Manage .new configuration files
    """
    def __init__(self):
        self.meta = _meta_
        self.msg = Msg()
        self.red = self.meta.color["RED"]
        self.green = self.meta.color["GREEN"]
        self.endc = self.meta.color["ENDC"]
        self.br = ""
        if self.meta.use_colors in ["off", "OFF"]:
            self.br = ")"
        self.etc = "/etc/"
        self.news = []

    def run(self):
        """print .new configuration files
        """
        self.find_new()
        for n in self.news:
            print("{0}".format(n))
        print("")
        self.msg.template(78)
        print("| Installed {0} new configuration files:".format(
            len(self.news)))
        self.msg.template(78)
        self.choices()

    def find_new(self):
        """Find all '.new' files from /etc/ folder
        and subfolders
        """
        print("\nSearch for .new configuration files:\n")
        for path, dirs, files in os.walk(self.etc):
            del dirs    # delete unsed
            for f in files:
                if f.endswith(".new"):
                    self.news.append(os.path.join(path, f))
        if not self.news:
            print("  No new configuration files\n")
            raise SystemExit()

    def choices(self):
        """Menu options for new configuration files
        """
        print("| {0}K{1}{2}eep the old and .new files, no changes".format(
            self.red, self.endc, self.br))
        print("| {0}O{1}{2}verwrite all old configuration files with new "
              "ones".format(self.red, self.endc, self.br))
        print("|  The old files will be saved with suffix .old")
        print("| {0}R{1}{2}emove all .new files".format(
            self.red, self.endc, self.br))
        print("| {0}P{1}{2}rompt K, O, R, D, M option for each single "
              "file".format(self.red, self.endc, self.br))
        print("| {0}Q{1}{2}uit from menu".format(self.red, self.endc, self.br))
        self.msg.template(78)
        try:
            choose = raw_input("\nWhat would you like to do [K/O/R/P/Q]? ")
        except EOFError:
            print("")
            raise SystemExit()
        print("")
        if choose in ("K", "k"):
            self.keep()
        elif choose in ("O", "o"):
            self.overwrite_all()
        elif choose in ("R", "r"):
            self.remove_all()
        elif choose in ("P", "p"):
            self.prompt()

    def overwrite_all(self):
        """Overwrite all .new files and keep
        old with suffix .old
        """
        for n in self.news:
            self._overwrite(n)

    def remove_all(self):
        """Remove all .new files
        """
        for n in self.news:
            self._remove(n)
        print("")

    def prompt(self):
        """Select file
        """
        self.msg.template(78)
        print("| Choose what to do file by file:")
        print("| {0}K{1}{2}eep, {3}O{4}{5}verwrite, {6}R{7}{8}emove, "
              "{9}D{10}{11}iff, {12}M{13}{14}erge, {15}Q{16}{17}uit".format(
                  self.red, self.endc, self.br, self.red, self.endc, self.br,
                  self.red, self.endc, self.br, self.red, self.endc, self.br,
                  self.red, self.endc, self.br, self.red, self.endc, self.br))
        self.msg.template(78)
        print("")
        self.i = 0
        try:
            while self.i < len(self.news):
                self.question(self.news[self.i])
                self.i += 1
        except EOFError:
            print("")
            raise SystemExit()

    def question(self, n):
        """Choose what do to file by file
        """
        print("")
        prompt_ask = raw_input("{0} [K/O/R/D/M/Q]? ".format(n))
        print("")
        if prompt_ask in ("K", "k"):
            self.keep()
        elif prompt_ask in ("O", "o"):
            self._overwrite(n)
        elif prompt_ask in ("R", "r"):
            self._remove(n)
        elif prompt_ask in ("D", "d"):
            self.diff(n)
            self.i -= 1
        elif prompt_ask in ("M", "m"):
            self.merge(n)
        elif prompt_ask in ("Q", "q", "quit"):
            self.quit()

    def _remove(self, n):
        """Remove one single file
        """
        if os.path.isfile(n):
            os.remove(n)
        if not os.path.isfile(n):
            print("File '{0}' removed".format(n))

    def _overwrite(self, n):
        """Overwrite old file with new and keep file with suffix .old
        """
        if os.path.isfile(n[:-4]):
            shutil.copy2(n[:-4], n[:-4] + ".old")
            print("Old file {0} saved as {1}.old".format(
                n[:-4].split("/")[-1], n[:-4].split("/")[-1]))
        if os.path.isfile(n):
            shutil.move(n, n[:-4])
            print("New file {0} overwrite as {1}".format(
                n.split("/")[-1], n[:-4].split("/")[-1]))

    def keep(self):
        pass

    def diff(self, n):
        """Print the differences between the two files
        """
        if os.path.isfile(n[:-4]):
            diff1 = Utils().read_file(n[:-4]).splitlines()
        if os.path.isfile(n):
            diff2 = Utils().read_file(n).splitlines()
        lines, l, c = [], 0, 0
        for a, b in itertools.izip_longest(diff1, diff2):
            l += 1
            if a != b:
                for s1, s2 in itertools.izip_longest(str(a), str(b)):
                    c += 1
                    if s1 != s2:
                        break
                print("@@ -{0},{1} +{2},{3} @@\n".format(l, c, l, c))
                for line in lines[-3:]:
                    print("{0}".format(line))
                if a is None:
                    a = ""
                print("{0}{1}{2}{3}".format(self.red, "-", self.endc, a))
                if b is None:
                    b = ""
                print("{0}{1}{2}{3}".format(self.green, "+", self.endc, b))
                lines = []
                c = 0
            else:
                lines.append(a)

    def merge(self, n):
        """Merge new file into old
        """
        if os.path.isfile(n[:-4]):
            old = Utils().read_file(n[:-4]).splitlines()
        if os.path.isfile(n):
            new = Utils().read_file(n).splitlines()
        with open(n[:-4], "w") as out:
            for l1, l2 in itertools.izip_longest(old, new):
                if l1 is None:
                    l1 = ""
                if l2 is None:
                    l2 = ""
                if l1 != l2:
                    out.write(l2 + "\n")
                else:
                    out.write(l1 + "\n")
            print("The file {0} merged in file {1}".format(
                n.split("/")[-1], n[:-4].split("/")[-1]))

    def quit(self):
        raise SystemExit()
