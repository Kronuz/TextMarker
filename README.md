# 🖍 Text Marker (Highlighter)

This plugin highlights words with different colors in Sublime Text.

Simply use <kbd>Alt</kbd>+<kbd>Space</kbd> to mark selected text.

![Description](screenshots/screenshot.gif?raw=true)


## Installation

- **_Recommended_** - Using [Sublime Package Control](https://packagecontrol.io "Sublime Package Control")
    - <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select `Package Control: Install Package`
    - install `Text Marker`
- Alternatively, download the package from [GitHub](https://github.com/Kronuz/TextMarker "TextMarker") into your `Packages` folder.


## Usage

- Step over any word in your document, all words will be highlighted.

- Being over a word or having some selection, press <kbd>Alt</kbd>+<kbd>Space</kbd> to mark all.

- <kbd>Alt</kbd>+<kbd>Escape</kbd> clears all marked text.

- Each time you mark a word a different color will be used (colors are configurable in the settings)


## Configuration

- Open settings using the command palette:
  `Preferences: TextMarker Settings - User`

- You can configure live highlight directly from the command palette:
  `TextMarker: Disable Live Highlight`

- You can add mouse mappings to be able to mark text by using <kbd>Ctrl</kbd>+<kbd>Click</kbd>;
  simply add the following Sublime Text "mousemaps":

```json
[
  { "button": "button1", "modifiers": ["alt"], "command": "text_marker", "press_command": "drag_select" },
  { "button": "button1", "count": 2, "modifiers": ["alt"], "command": "text_marker_clear", "press_command": "drag_select" }
]
```


## Donate

[![Click here to lend your support to TextMarker and make a donation!](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.me/Kronuz/25)


## License

Copyright (C) 2018 German Mendez Bravo (Kronuz). All rights reserved.

MIT license

This plugin was initially a fork of
https://github.com/SublimeText/WordHighlight/blob/master/word_highlight.py
