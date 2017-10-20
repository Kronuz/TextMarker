import os
import re

import sublime
import sublime_plugin

from .colors import names_to_hex, xterm_to_hex
all_names_to_hex = dict(names_to_hex, **xterm_to_hex)

version = "1.1"


ALL_SETTINGS = [
    'word_highlights',
    'word_highlights_default_color',
    'word_highlights_live_color',
    'word_highlights_draw_outlined',
    'word_highlights_when_selection_is_empty',
]


def log(s):
    # print("[WordHighlights]", s)
    pass


class HtmlGen:
    name = "Color"
    prefix = "col_"
    backup_ext = ".chback"

    colors = {}
    color_scheme = None
    need_upd = False
    need_restore = False
    need_backup = False
    gen_string = """
        <dict>
            <key>name</key>
            <string>{name}</string>
            <key>scope</key>
            <string>{scope}</string>
            <key>settings</key>
            <dict>
                <key>background</key>
                <string>{background}</string>
                <key>foreground</key>
                <string>{foreground}</string>
            </dict>
        </dict>
"""

    def normalize(self, col):
        if col:
            col = all_names_to_hex.get(col.lower(), col.upper())
            if col.startswith('0X'):
                col = '#' + col[2:]
            try:
                if col[0] != '#':
                    raise ValueError
                if len(col) == 4:
                    col = '#' + col[1] * 2 + col[2] * 2 + col[3] * 2 + 'FF'
                elif len(col) == 5:
                    col = '#' + col[1] * 2 + col[2] * 2 + col[3] * 2 + col[4] * 2
                elif len(col) == 7:
                    col += 'FF'
                return '#%02X%02X%02X%02X' % (int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16), int(col[7:9], 16))
            except Exception:
                print("Invalid color: %r" % col)

    def write_file(self, pp, fl, s):
        rf = pp + fl
        dn = os.path.dirname(rf)
        if not os.path.exists(dn):
            os.makedirs(dn)
        f = open(rf, 'w')
        f.write(s)
        f.close()

    def read_file(self, pp, fl):
        rf = pp + fl
        if os.path.exists(rf):
            f = open(rf, 'r')
            res = f.read()
            f.close()
        else:
            rf = 'Packages' + fl
            res = sublime.load_resource(rf)
        return res

    def get_inv_col(self, col):
        # [https://stackoverflow.com/a/3943023]
        r = int(col[1:3], 16) / 255.0
        g = int(col[3:5], 16) / 255.0
        b = int(col[5:7], 16) / 255.0
        # a = int(col[7:9], 16) / 255.0
        l = 0.2126 * r + 0.7152 * g + 0.0722 * b

        if l < 0.060:
            return '#66666FF'

        if l < 0.089:
            return '#888888FF'

        if l < 0.179:
            return '#BBBBBBFF'

        if l < 0.358:
            return '#EEEEEEFF'

        if l < 0.537:
            return '#222222FF'

        if l < 0.716:
            return '#222222FF'

        return '#222222FF'

    def region_name(self, s):
        return self.prefix + s[1:]

    def add_color(self, col):
        col = self.normalize(col)
        if not col:
            return
        if col not in self.colors:
            self.colors[col] = self.region_name(col)
            self.need_upd = True
        return self.colors[col]

    def need_update(self):
        return self.need_upd

    def color_scheme_path(self, view):
        packages_path = sublime.packages_path()
        cs = self.color_scheme
        if cs is None:
            self.color_scheme = view.settings().get('color_scheme')
            cs = self.color_scheme
        # do not support empty color scheme
        if not cs:
            log("Empty scheme")
            return
        # extract name
        cs = cs[cs.find('/'):]
        return packages_path, cs

    def get_color_scheme(self, packages_path, cs):
        cont = self.read_file(packages_path, cs)
        if os.path.exists(packages_path + cs + self.backup_ext):
            log("Already backuped")
        else:
            self.write_file(packages_path, cs + self.backup_ext, cont)  # backup
            log("Backup done")
        return cont

    def update(self, view):
        if not self.need_upd:
            return
        self.need_upd = False

        color_scheme_path = self.color_scheme_path(view)
        if not color_scheme_path:
            return
        packages_path, cs = color_scheme_path
        cont = self.get_color_scheme(packages_path, cs)

        current_colors = set("#%s" % c for c in re.findall(r'<string>%s(.*?)</string>' % self.prefix, cont, re.DOTALL))

        string = ""
        for col, name in self.colors.items():
            if col not in current_colors:
                fg_col = self.get_inv_col(col)
                string += self.gen_string.format(
                    name=self.name,
                    scope=name,
                    background=col,
                    foreground=fg_col,
                )

        if string:
            # edit cont
            n = cont.find("<array>") + len("<array>")
            try:
                cont = cont[:n] + string + cont[n:]
            except UnicodeDecodeError:
                cont = cont[:n] + string.encode("utf-8") + cont[n:]

            self.write_file(packages_path, cs, cont)
            self.need_restore = True
            log("Updated")

    def restore_color_scheme(self):
        if not self.need_restore:
            return
        self.need_restore = False
        cs = self.color_scheme
        # do not support empty color scheme
        if not cs:
            log("Empty scheme, can't restore")
            return
        # extract name
        cs = cs[cs.find('/'):]
        packages_path = sublime.packages_path()
        if os.path.exists(packages_path + cs + self.backup_ext):
            log("Starting restore scheme: " + cs)
            # TODO: move to other thread
            self.write_file(packages_path, cs, self.read_file(packages_path, cs + self.backup_ext))
            self.colors = {}
            log("Restore done.")
        else:
            log("No backup :(")

    def set_color_scheme(self, view):
        settings = view.settings()
        cs = settings.get('color_scheme')
        if cs != self.color_scheme:
            color_scheme_path = self.color_scheme_path(view)
            if color_scheme_path:
                packages_path, cs = color_scheme_path
                cont = self.get_color_scheme(packages_path, cs)
                self.colors = dict(("#%s" % c, "%s%s" % (self.prefix, c)) for c in re.findall(r'<string>%s(.*?)</string>' % self.prefix, cont, re.DOTALL))
            self.color_scheme = settings.get('color_scheme')
            self.need_backup = True

    def change_color_scheme(self, view):
        cs = view.settings().get('color_scheme')
        if cs and cs != self.color_scheme:
            log("Color scheme changed %s -> %s" % (self.color_scheme, cs))
            self.restore_color_scheme()
            self.set_color_scheme(view)
            self.update(view)

htmlGen = HtmlGen()


def settings_changed():
    for window in sublime.windows():
        for view in window.views():
            reload_settings(view.settings())


def reload_settings(settings):
    '''Restores user settings.'''
    settings_name = 'WordHighlights'
    global_settings = sublime.load_settings(settings_name + '.sublime-settings')
    global_settings.clear_on_change(settings_name)
    global_settings.add_on_change(settings_name, settings_changed)

    for setting in ALL_SETTINGS:
        if global_settings.has(setting):
            settings.set(setting, global_settings.get(setting))

    if not settings.has('word_highlights'):
        settings.set('word_highlights', True)

    if not settings.has('word_highlights_default_color'):
        settings.set('word_highlights_default_color', "")

    if not settings.has('word_highlights_live_color'):
        settings.set('word_highlights_live_color', settings.get('word_highlights_default_color'))

    if not settings.has('word_highlights_when_selection_is_empty'):
        settings.set('word_highlights_when_selection_is_empty', False)


def get_setting(settings, name):
    if not settings.has(name):
        reload_settings(settings)
    return settings.get(name)


def regex_escape(string):
    outstring = ""
    for c in string:
        if c != '\\':
            outstring += '[' + c + ']'
        else:
            outstring += '\\'
    return outstring


def highlight(view, color=None, when_selection_is_empty=False, add_selections=False):
    settings = view.settings()
    draw_outlined = sublime.DRAW_OUTLINED if get_setting(settings, 'word_highlights_draw_outlined') else 0
    word_separators = settings.get('word_separators')

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

    color_scope_name = htmlGen.add_color(color) or 'comment'
    if htmlGen.need_update():
        htmlGen.update(view)
    view.add_regions('wh_' + color_scope_name, regions, color_scope_name, '', draw_outlined | sublime.PERSISTENT)

    if add_selections:
        view_sel.add_all(regions)


def reset(view):
    for color_scope_name in htmlGen.colors.values():
        view.erase_regions('wh_' + color_scope_name)


# command to restore color scheme
class RestoreColorSchemeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        htmlGen.restore_color_scheme()


class WordHighlightsListener(sublime_plugin.EventListener):
    def on_new(self, view):
        htmlGen.set_color_scheme(view)
        view.settings().add_on_change('color_scheme', lambda self=self, view=view: htmlGen.change_color_scheme(view))

    def on_selection_modified(self, view):
        settings = view.settings()
        if get_setting(settings, 'word_highlights'):
            color = get_setting(settings, 'word_highlights_live_color')
            when_selection_is_empty = get_setting(settings, 'word_highlights_when_selection_is_empty')
            highlight(view, color=color, when_selection_is_empty=when_selection_is_empty)


class WordHighlightsToggleCommand(sublime_plugin.TextCommand):
    _word_highlights = None
    _word_highlights_when_selection_is_empty = None

    def run(self, edit, block=False):
        settings = self.view.settings()
        _word_highlights = get_setting(settings, 'word_highlights')
        _word_highlights_when_selection_is_empty = get_setting(settings, 'word_highlights_when_selection_is_empty')
        if self.__class__._word_highlights is None:
            self.__class__._word_highlights = _word_highlights
        if self.__class__._word_highlights_when_selection_is_empty is None:
            self.__class__._word_highlights_when_selection_is_empty = _word_highlights_when_selection_is_empty
        if _word_highlights_when_selection_is_empty and _word_highlights:
            settings.set('word_highlights', self.__class__._word_highlights)
            settings.set('word_highlights_when_selection_is_empty', self.__class__._word_highlights_when_selection_is_empty)
            reset(self.view)
        else:
            settings.set('word_highlights', True)
            settings.set('word_highlights_when_selection_is_empty', True)
            color = get_setting(settings, 'word_highlights_default_color')
            highlight(self.view, color=color, when_selection_is_empty=True)


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
                settings = self.view.settings()
                color = get_setting(settings, 'word_highlights_default_color')
            highlight(self.view, color=color, when_selection_is_empty=True)

    def on_done(self, color):
        if color:
            highlight(self.view, color=color, when_selection_is_empty=True)
