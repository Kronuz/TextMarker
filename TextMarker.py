from __future__ import absolute_import

import sublime
import sublime_plugin
from itertools import chain

from .settings import Settings, SettingTogglerCommandMixin
from .colorizer import SchemaColorizer

NAME = "TextMarker"
VERSION = "1.0.3"

DEFAULT_COLORS = ['comment']


def regex_escape(string):
    outstring = ""
    for c in string:
        if c != '\\':
            outstring += '[' + c + ']'
        else:
            outstring += '\\'
    return outstring


def highlight(view, color=None, when_selection_is_empty=False, add_selections=False, prefix='wh_'):
    view_settings = view.settings()
    word_separators = view_settings.get('word_separators')

    all_regions = {}
    for color_scope_name in chain(colorizer.colors.values(), DEFAULT_COLORS):
        regions = view.get_regions(prefix + color_scope_name)
        if regions:
            all_regions[color_scope_name] = regions

    def find_color(sel):
        for color_scope_name, regions in all_regions.items():
            for region in regions:
                if region.contains(sel):
                    return color_scope_name

    colors = set()
    view_sel = view.sel()
    regions = []
    for sel in view_sel:
        # Figure out what colors are currently active in the selection
        color_scope_name = find_color(sel)
        if color_scope_name:
            colors.add(color_scope_name)
        if sel:
            # If the selection is a range...
            string = view.substr(sel).strip()
            if string:
                # If we directly compare sel and view.word(sel), then in compares their
                # a and b values rather than their begin() and end() values. This means
                # that a leftward selection (with a > b) will never match the view.word()
                # of itself. As a workaround, we compare the lengths instead.
                if len(sel) == len(view.word(sel)):
                    regex = '\\b' + regex_escape(string) + '\\b'
                else:
                    regex = regex_escape(string)
                regions.extend(view.find_all(regex))
        else:
            # If selection is a point...
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

    if prefix == 'wh_' and colors:
        for color_scope_name in colors:
            view.erase_regions(prefix + color_scope_name)
    else:
        if not color:
            for c in settings.get('default_colors') or DEFAULT_COLORS:
                csn = colorizer.add_color(c)
                if csn and csn not in all_regions:
                    color = c
                    break
        color_scope_name = colorizer.add_color(color) or 'comment'
        if colorizer.need_update():
            colorizer.update(view)
        view.add_regions(prefix + color_scope_name, regions, color_scope_name, '', (sublime.DRAW_OUTLINED if settings.get('draw_outlined') else 0))

    if add_selections:
        view_sel.add_all(regions)


def clear(view=None, prefix='wh_'):
    if view:
        for color_scope_name in chain(colorizer.colors.values(), ['comment']):
            view.erase_regions(prefix + color_scope_name)
    else:
        for window in sublime.windows():
            for view in window.views():
                clear(view)


# command to restore color scheme
class TextMarkerRestoreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clear()
        colorizer.restore_color_scheme()


class TextMarkerListener(sublime_plugin.EventListener):
    live = False

    def on_new(self, view):
        colorizer.set_color_scheme(view)
        view.settings().add_on_change('color_scheme', lambda self=self, view=view: colorizer.change_color_scheme(view))

    def on_selection_modified(self, view):
        if settings.get('live'):
            self.live = True
            color = settings.get('live_color') or 'comment'
            when_selection_is_empty = settings.get('when_selection_is_empty')
            highlight(view, color=color, when_selection_is_empty=when_selection_is_empty, prefix='whl_')
        elif self.live:
            clear(view, prefix='whl_')
            self.live = False


class TextMarkerClearCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        clear()


class TextMarkerResetCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        clear()
        colorizer.clear()


class TextMarkerCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False, color=None):
        if color == "<select>":
            highlight(self.view, when_selection_is_empty=True, add_selections=True)
        elif color == "<input>":
            self.view.window().show_input_panel("Color:", "", self.on_done, None, None)
        else:
            highlight(self.view, color=color, when_selection_is_empty=True)

    def on_done(self, color):
        if color:
            highlight(self.view, color=color, when_selection_is_empty=True)


################################################################################
# Initialize settings and main objects only once
class TextMarkerSettings(Settings):
    pass


settings = TextMarkerSettings(NAME)


class TextMarkerToggleSettingCommand(SettingTogglerCommandMixin, sublime_plugin.WindowCommand):
    settings = settings


if 'colorizer' not in globals():
    colorizer = SchemaColorizer()


################################################################################

def plugin_loaded():
    settings.load()


# ST3 features a plugin_loaded hook which is called when ST's API is ready.
#
# We must therefore call our init callback manually on ST2. It must be the last
# thing in this plugin (thanks, beloved contributors!).
if int(sublime.version()) < 3000:
    plugin_loaded()
