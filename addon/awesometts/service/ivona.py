# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
#
# Copyright (C) 2016       Anki AwesomeTTS Development Team
# Copyright (C) 2016       Dave Shifflett
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
Service implementation for the IVONA API
"""

from .base import Service
import sys
sys.path.append('C:\Python27\Lib')
sys.path.append('C:\Python27\Lib\site-packages')
import pyvona

__all__ = ['IVONA']


VOICES = {
    'Salli': ('en-US', 'female'),
    'Joey': ('en-US', 'male'),
}


class IVONA(Service):
    """
    Provides a Service-compliant implementation for IVONA.
    """

    __slots__ = [
    ]

    NAME = "IVONA"

    # Although IVONA is an Internet service, we do not mark it with
    # Trait.INTERNET, as it is a paid-for-by-the-user API, and we do not want
    # to rate-limit it or trigger error caching behavior
    TRAITS = []

    def desc(self):
        """Returns name with a voice count."""

        return "IVONA API (%d voices)" % len(VOICES)

    def extras(self):
        """The IVONA API requires access key and secret key."""

        return [dict(key='access', label="Access Key", required=True),
                dict(key='secret', label="Secret Key", required=True)]

    def options(self):
        """Provides access to voice only."""

        voice_lookup = {self.normalize(api_name): api_name
                        for api_name in VOICES.keys()}

        def transform_voice(user_value):
            """Fixes whitespace and casing only."""
            normalized_value = self.normalize(user_value)
            return (voice_lookup[normalized_value]
                    if normalized_value in voice_lookup else user_value)

        return [
            dict(key='voice',
                 label="Voice",
                 values=[(api_name,
                          "%s (%s %s)" % (api_name, gender, language))
                         for api_name, (language, gender)
                         in sorted(VOICES.items(),
                                   key=lambda item: (item[1][0],
                                                     item[1][1]))],
                 transform=transform_voice),

            dict(key='speed',
                 label="Speed",
                 values=(-10, +10),
                 transform=lambda i: min(max(-10, int(round(float(i)))), +10),
                 default=0),

            dict(key='pitch',
                 label="Pitch",
                 values=(0, +200),
                 transform=lambda i: min(max(0, int(round(float(i)))), +200),
                 default=100),
        ]

    def run(self, text, options, path):
        """Downloads from IVONA API directly to an MP3."""

        v = pyvona.create_voice(options['access'], options['secret'])
        v.codec = 'mp3'
        v.voice_name = options['voice']
        v.fetch_voice(text, path)

        #  self.net_reset()  # no throttle; FIXME should be controlled by trait
