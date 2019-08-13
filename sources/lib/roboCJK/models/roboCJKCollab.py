"""
Copyright 2019 Black Foundry.

This file is part of Robo-CJK.

Robo-CJK is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robo-CJK is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Robo-CJK.  If not, see <https://www.gnu.org/licenses/>.
"""
class RoboCJKCollab(object):
    def __init__(self):
        self._lockers = []
        self._user = ''

    @property
    def lockers(self):
        return [locker for locker in self._lockers]
    
    def _userLocker(self, user):
        l = [locker for locker in self._lockers if locker.user == user]
        if not l: return
        return l[0]

    def _addLocker(self, user):
        if user not in [locker.user for locker in self._lockers]:
            locker = Locker(self, user)
            self._lockers.append(Locker(self, user))
        else:
            locker = self._userLocker(user)
        return locker

    @property
    def _toDict(self):
        return {e: [l._toDict for l in getattr(self, e)] for e in dir(self) if not e.startswith('_')}


class Locker(object):
    def __init__(self, controller, user):
        self._controller = controller
        self.user = user
        self._glyphs = set()

    @property
    def _allOtherLockedGlyphs(self):
        s = set()
        for locker in self._controller._lockers:
            s |= locker._glyphs
        s -= self._glyphs
        return s
    
    @property
    def glyphs(self):
        return list(self._glyphs)
    

    def _addGlyphs(self, glyphs):
        for glyph in glyphs:
            if glyph not in self._allOtherLockedGlyphs:
                self._glyphs.add(glyph)

    def _removeGlyphs(self, glyphs):
        for glyph in glyphs:
            if glyph in self._glyphs:
                self._glyphs.remove(glyph)

    @property
    def _toDict(self):
        return {e: getattr(self, e) for e in dir(self) if not e.startswith('_')}


import random
def testCollab(users):
    collab = RoboCJKCollab()
    for user in users:
        collab._addLocker(user)
    for locker in collab.lockers:
        locker._addGlyphs(['glyph_%s'%random.randint(0, 3) for i in range(3)])
    for locker in collab.lockers:
        print(locker._toDict)

    print(collab._toDict)

if __name__ == "__main__":
    testCollab(['user1', 'user2'])

