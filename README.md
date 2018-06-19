# 🖍 Text Marker (Highlighter)

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/Kronuz/25)
[![Package Control](https://img.shields.io/packagecontrol/dt/Text%20Marker.svg)](https://packagecontrol.io/packages/Text%20Marker)

This Sublime Text plugin allows temporarily and persistently marking all
occurrences of selected words in a color; multiple marked selections can be
added simultaneously, each marking the selections with different colors.

Optionally (enabled by default) it also highlights all copies of a word that
currently has the insertion cursor upon it or which is currently selected.

Simply use <kbd>Alt</kbd>+<kbd>Space</kbd> to mark selected text.

![Description](screenshots/screenshot.gif?raw=true)


## Installation

- **_Recommended_** - Using [Sublime Package Control](https://packagecontrol.io "Sublime Package Control")
    - <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select `Package Control: Install Package`
    - install `Text Marker`
- Alternatively, download the package from [GitHub](https://github.com/Kronuz/TextMarker "TextMarker") into your `Packages` folder.


## Usage

- Step over any word in your document, all occurrences of the word will be highlighted.

- Being over a word or having some selection, press <kbd>Alt</kbd>+<kbd>Space</kbd> to mark all.

- <kbd>Alt</kbd>+<kbd>Escape</kbd> clears all marked text.

- Each time you mark a word a different color will be used (colors are configurable in the settings)


## Configuration

- Open settings using the command palette:
  `Preferences: TextMarker Settings - User`

- You can configure live word highlight directly from the command palette:
  `TextMarker: Disable Live Highlight`

- You can add mouse mappings to be able to mark text by using <kbd>Ctrl</kbd>+<kbd>Click</kbd>;
  simply add the following Sublime Text "mousemaps":

```json
[
  { "button": "button1", "modifiers": ["alt"], "command": "text_marker", "press_command": "drag_select" },
  { "button": "button1", "count": 2, "modifiers": ["alt"], "command": "text_marker_clear", "press_command": "drag_select" }
]
```


## License

Copyright (C) 2018 German Mendez Bravo (Kronuz). All rights reserved.

MIT license

This plugin was initially a fork of
https://github.com/SublimeText/WordHighlight/blob/master/word_highlight.py
