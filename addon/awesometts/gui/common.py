# -*- coding: utf-8 -*-
# pylint:disable=bad-continuation

# AwesomeTTS text-to-speech add-on for Anki
#
# Copyright (C) 2010-2014  Anki AwesomeTTS Development Team
# Copyright (C) 2010-2012  Arthur Helfstein Fragoso
# Copyright (C) 2013-2014  Dave Shifflett
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

"""
Common reusable GUI elements

Provides menu action and button classes.

As everything done from the add-on code has to do with AwesomeTTS, these
all carry a speaker icon (if supported by the desktop environment).
"""

__all__ = ['ICON', 'Action', 'Button', 'Filter']

from PyQt4 import QtCore, QtGui


ICON = QtGui.QIcon(':/icons/speaker.png')

SHORTCUT = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_T)

NO_SHORTCUT = QtGui.QKeySequence()


class _Connector(object):  # used like a mixin, pylint:disable=R0903
    """
    Handles deferring construction of the target class until it's
    needed and then keeping a reference to it as long as its triggering
    GUI element still exists.
    """

    def __init__(self, signal, target):
        """
        Store the target for future use and wire up the passed signal.
        """

        self._target = target
        self._instance = None

        signal.connect(self._show)

    def _show(self):
        """
        If the target has not yet been constructed, do so now, and then
        show it.
        """

        if not self._instance:
            self._instance = self._target.constructor(
                *self._target.args,
                **self._target.kwargs
            )

        self._instance.show()


class Action(QtGui.QAction, _Connector):
    """
    Provides a menu action to show a dialog when triggered.
    """

    def muzzle(self, disable):
        """
        If disable is True, then this shortcut will be temporarily
        disabled (i.e. muzzled), but the action will remain available
        if it would normally be.
        """

        self.setShortcut(NO_SHORTCUT if disable else SHORTCUT)

    def __init__(self, target, text, parent):
        """
        Initializes the menu action and wires its 'triggered' event.

        If the specified parent is a QMenu, this new action will
        automatically be added to it.
        """

        QtGui.QAction.__init__(self, ICON, text, parent)
        _Connector.__init__(self, self.triggered, target)

        self.setShortcut(SHORTCUT)

        if isinstance(parent, QtGui.QMenu):
            parent.addAction(self)


class Button(QtGui.QPushButton, _Connector):
    """
    Provides a button to show a dialog when clicked.
    """

    def __init__(self, target, tooltip, text=None, style=None):
        """
        Initializes the button and wires its 'clicked' event.

        Note that buttons that have text get one set of styling
        different from ones without text.
        """

        QtGui.QPushButton.__init__(self, ICON, text)
        _Connector.__init__(self, self.clicked, target)

        if text:
            self.setIconSize(QtCore.QSize(15, 15))

        else:
            self.setFixedWidth(20)
            self.setFixedHeight(20)
            self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.setShortcut(SHORTCUT)
        self.setToolTip(
            "%s (%s)" %
            (tooltip, SHORTCUT.toString(QtGui.QKeySequence.NativeText))
        )

        if style:
            self.setStyle(style)


class Filter(QtCore.QObject):
    """
    Once instantiated, serves as an installEventFilter-compatible object
    instance that supports filtering events with a condition.
    """

    def __init__(self, relay, when, *args, **kwargs):
        """
        Make a filter that will "relay" onto a callable "when" a certain
        condition is met (both callables accepting an event argument).
        """

        super(Filter, self).__init__(*args, **kwargs)
        self._relay = relay
        self._when = when

    def eventFilter(self, _, event):  # pylint: disable=invalid-name
        """
        Qt eventFilter method. Returns True if the event has been
        handled and should be filtered out.

        The result of and'ing the return values from the `when` and
        `relay` callable is forced to a boolean if it is not already (as
        Qt blows up quite spectacularly if it is not).
        """

        return bool(self._when(event) and self._relay(event))