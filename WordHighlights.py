from __future__ import absolute_import

import sublime
import sublime_plugin

from .settings import Settings, SettingTogglerCommandMixin
from .colorizer import SchemaColorizer

NAME = "WordHighlights"  # SublimeHighlighter
VERSION = "2.0"

colorizer = SchemaColorizer()


def regex_escape(string):
    outstring = ""
    for c in string:
        if c != '\\':
            outstring += '[' + c + ']'
        else:
            outstring += '\\'
    return outstring


def highlight(view, color=None, when_selection_is_empty=False, add_selections=False):
    view_settings = view.settings()
    word_separators = view_settings.get('word_separators')

    draw_outlined = sublime.DRAW_OUTLINED if settings.get('draw_outlined') else 0

    view_sel = view.sel()
    regions = []
    for sel in view_sel:
        # If we directly compare sel and view.word(sel), then in compares their
        # a and b values rather than their begin() and end() values. This means
        # that a leftward selection (with a > b) will never match the view.word()
        # of itself.
        # As a workaround, we compare the lengths instead.
        if sel:
            string = view.substr(sel).strip()
            if string:
                if len(sel) == len(view.word(sel)):
                    regex = '\\b' + regex_escape(string) + '\\b'
                else:
                    regex = regex_escape(string)
                regions.extend(view.find_all(regex))
        else:
            if when_selection_is_empty:
                string = view.substr(view.word(sel)).strip()
                if string and any(c not in word_separators for c in string):
                    regions.extend(view.find_all('\\b' + regex_escape(string) + '\\b'))

    if not regions and len(view_sel) > 1:
        regions = list(view_sel)

    if regions:
        sublime.status_message("%d region%s selected" % (len(regions), "" if len(regions) == 1 else "s"))
    else:
        sublime.status_message("")

    color_scope_name = colorizer.add_color(color) or 'comment'
    if colorizer.need_update():
        colorizer.update(view)
    view.add_regions('wh_' + color_scope_name, regions, color_scope_name, '', draw_outlined | sublime.PERSISTENT)

    if add_selections:
        view_sel.add_all(regions)


def reset(view):
    for color_scope_name in colorizer.colors.values():
        view.erase_regions('wh_' + color_scope_name)


# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        colorizer.restore_color_scheme()


class WordHighlightsListener(sublime_plugin.EventListener):
    def on_new(self, view):
        colorizer.set_color_scheme(view)
        view.settings().add_on_change('color_scheme', lambda self=self, view=view: colorizer.change_color_scheme(view))

    def on_selection_modified(self, view):
        if settings.get('live'):
            color = settings.get('live_color')
            when_selection_is_empty = settings.get('when_selection_is_empty')
            highlight(view, color=color, when_selection_is_empty=when_selection_is_empty)


class WordHighlightsResetCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        reset(self.view)


class WordHighlightsCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False, color=None):
        if color == "<select>":
            highlight(self.view, when_selection_is_empty=True, add_selections=True)
        elif color == "<input>":
            self.view.window().show_input_panel("Color:", "", self.on_done, None, None)
        else:
            if not color:
                color = settings.get('default_color')
            highlight(self.view, color=color, when_selection_is_empty=True)

    def on_done(self, color):
        if color:
            highlight(self.view, color=color, when_selection_is_empty=True)


################################################################################
# Initialize settings and main objects only once
class WordHighlightsSettings(Settings):
    pass


if 'settings' not in globals():
    settings = WordHighlightsSettings(NAME)

    class WordHighlightsToggleSettingCommand(SettingTogglerCommandMixin, sublime_plugin.WindowCommand):
        settings = settings


################################################################################

def plugin_loaded():
    settings.load()


# ST3 features a plugin_loaded hook which is called when ST's API is ready.
#
# We must therefore call our init callback manually on ST2. It must be the last
# thing in this plugin (thanks, beloved contributors!).
if int(sublime.version()) < 3000:
    plugin_loaded()
