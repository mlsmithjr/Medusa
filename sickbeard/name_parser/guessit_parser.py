#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Guessit Name Parser."""
from __future__ import unicode_literals

import guessit
import six


class GuessitNameParser(object):
    """Guessit Name Parser."""

    expected_titles = {
        # guessit doesn't add dots for this show
        '11.22.63',

        # guessit gets confused because of the numbers (only in some special cases)
        # (?<![^/\\]) means -> it matches nothing but path separators  (negative lookbehind)
        r're:(?<![^/\\])12 Monkeys\b',
        r're:(?<![^/\\])500 Bus Stops\b',
        r're:(?<![^/\\])60 Minutes\b',
        r're:(?<![^/\\])Star Trek DS9\b',
        r're:(?<![^/\\])The 100\b',

        # guessit: conflicts with italian language
        r're:(?<![^/\\])\w+ it\b',
    }

    # release group exception list
    expected_groups = {
        # https://github.com/guessit-io/guessit/issues/297
        # guessit blacklists parts of the name for the following groups
        r're:\bbyEMP\b',
        r're:\bELITETORRENT\b',
        r're:\bNovaRip\b',
        r're:\bPARTiCLE\b',
        r're:\bPOURMOi\b',
        r're:\bRipPourBox\b',
        r're:\bRiPRG\b',

        # https://github.com/guessit-io/guessit/issues/316
        r're:\bCDP\b',
        r're:\bCDD\b',

        # https://github.com/guessit-io/guessit/issues/317
        r're:\bHDD\b',

        # release groups with numbers
        r're:\b4EVERHD\b',  # remove after guessit #313 is fixed
        r're:\bF4ST3R\b',
        r're:\bF4ST\b',
        r're:\bPtM\b',
        r're:\bTGNF4ST\b',
        r're:\bTV2LAX9\b',
    }

    allowed_languages = {
        'de',
        'en',
        'es',
        'fr',
        'he',
        'hu',
        'it',
        'jp',
        'nl',
        'pl',
        'pt',
        'ro',
        'ru',
        'sv',
        'uk',
    }

    allowed_countries = {
        'us',
        'gb',
    }

    allow_multi_season = False

    def guess(self, name, show_type=None):
        """Guess the episode information from a given release name.

        :param name: the release name
        :type name: str
        :param show_type: None, regular or anime
        :type show_type: str
        :return: the guessed properties
        :rtype: dict
        """
        options = dict(type='episode', implicit=True, show_type=show_type, episode_prefer_number=show_type == 'anime',
                       expected_title=normalize(self.expected_titles),
                       expected_group=normalize(self.expected_groups),
                       allowed_languages=normalize(self.allowed_languages),
                       allowed_countries=normalize(self.allowed_countries))
        return guessit.guessit(name, options=options)

    def parse(self, name, show_type=None):
        """Guess the episode information from a given release name.

        Same as self.guess(..) method but returns a dictionary with keys and values according to ParseResult
        :param name:
        :type name: str
        :param show_type: 'regular' or 'anime'
        :type show_type: str
        :return:
        :rtype: dict
        """
        guess = self.guess(name, show_type=show_type)

        result = {
            'original_name': name,
            'series_name': guess.get('alias') or guess.get('title'),
            'season_number': single_or_list(guess.get('season'), self.allow_multi_season),
            'release_group': guess.get('release_group'),
            'air_date': guess.get('date'),
            'version': guess.get('version', -1),
            'extra_info': ' '.join(ensure_list(guess.get('other'))) if guess.get('other') else None,
            'episode_numbers': ensure_list(guess.get('episode')),
            'ab_episode_numbers': ensure_list(guess.get('absolute_episode'))
        }

        return result


def single_or_list(value, allow_multi):
    """Return a single value or a list.

    If value is a list with more than one element and allow_multi is False then it returns None.
    :param value:
    :type value: list
    :param allow_multi: if False, multiple values will return None
    :type allow_multi: bool
    :rtype: list
    """
    if not isinstance(value, list):
        return value

    if allow_multi:
        return sorted(value)


def ensure_list(value):
    """Return a list.

    When value is not a list, return a list containing the single value.
    :param value:
    :rtype: list
    """
    return sorted(value) if isinstance(value, list) else [value] if value is not None else []


def normalize(strings):
    """Normalize string as expected by guessit.

    Remove when https://github.com/guessit-io/guessit/issues/326 is fixed.
    :param strings:
    :rtype: list of str
    """
    result = []
    for string in strings:
        if six.PY2 and isinstance(string, six.text_type):
            string = string.encode('utf-8')
        elif six.PY3 and isinstance(string, six.binary_type):
            string = string.decode('ascii')
        result.append(string)
    return result


parser = GuessitNameParser()
