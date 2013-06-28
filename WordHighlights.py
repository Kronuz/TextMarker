import sublime
import sublime_plugin

DEFAULT_COLOR_SCOPE_NAME = ['comment']

ALL_SETTINGS = [
    'word_highlights',
    'word_highlights_color_scope_name',
    'word_highlights_draw_outlined',
    'word_highlights_when_selection_is_empty',
]


def settings_changed():
    for window in sublime.windows():
        for view in window.views():
            reload_settings(view)


def reload_settings(view):
    '''Restores user settings.'''
    settings = sublime.load_settings(__name__ + '.sublime-settings')
    settings.clear_on_change(__name__)
    settings.add_on_change(__name__, settings_changed)

    for setting in ALL_SETTINGS:
        if settings.get(setting) is not None:
            view.settings().set(setting, settings.get(setting))

    if view.settings().get('word_highlights') is None:
        view.settings().set('word_highlights', True)


def regex_escape(string):
    outstring = ""
    for c in string:
        if c != '\\':
            outstring += '[' + c + ']'
        else:
            outstring += '\\'
    return outstring


def highlight(view, current=0, when_selection_is_empty=False):
    settings = view.settings()
    color_scope_name = settings.get('word_highlights_color_scope_name', DEFAULT_COLOR_SCOPE_NAME)
    draw_outlined = bool(settings.get('word_highlights_draw_outlined')) * sublime.DRAW_OUTLINED
    word_separators = settings.get('word_separators')

    if len(view.sel()) > 1:
        regions = list(view.sel())
    else:
        regions = []
        for sel in view.sel():
            #If we directly compare sel and view.word(sel), then in compares their
            #a and b values rather than their begin() and end() values. This means
            #that a leftward selection (with a > b) will never match the view.word()
            #of itself.
            #As a workaround, we compare the lengths instead.
            if len(sel) == 0:
                if when_selection_is_empty:
                    string = view.substr(view.word(sel)).strip()
                    if len(string) and all([not c in word_separators for c in string]):
                        regions += view.find_all('\\b' + regex_escape(string) + '\\b')
            else:
                string = view.substr(sel).strip()
                if len(string):
                    if len(sel) == len(view.word(sel)):
                        regions += view.find_all('\\b' + regex_escape(string) + '\\b')
                    else:
                        regions += view.find_all(regex_escape(string))
    view.add_regions('WordHighlights%s' % current, regions, color_scope_name[current % len(color_scope_name)], draw_outlined)


def reset(view):
    settings = view.settings()
    color_scope_name = settings.get('word_highlights_color_scope_name', DEFAULT_COLOR_SCOPE_NAME)
    for current in range(len(color_scope_name)):
        view.erase_regions('WordHighlights%s' % current)


class WordHighlightsListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        settings = view.settings()
        if settings.get('word_highlights', True):
            highlight(view, 0, settings.get('word_highlights_when_selection_is_empty', False))

    def on_load(self, view):
        reload_settings(view)


class WordHighlightsResetCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        reset(self.view)


class WordHighlightsCommand(sublime_plugin.TextCommand):
    def run(self, edit, block=False, current=0):
        highlight(self.view, current, True)
