# 🖍 Text Marker (Highlighter)

this plugin highlights words with different colors in Sublime Text.


## Installation

- **_Recommended_** - Using [Sublime Package Control](https://packagecontrol.io "Sublime Package Control")
    - <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> then select `Package Control: Install Package`
    - install `Text Marker`
- Alternatively, download the package from [GitHub](https://github.com/Kronuz/TextMarker "TextMarker") into your `Packages` folder.


## Usage

- Over the work that you want to mark, press `alt+space`.

- `alt+escape` clears all marked text.

- You can make a specific selection(s) to mark.

- Each time you mark a word a different color will be used (colors are configurable in the settings)


## Configuration

You can add mouse mappings to be able to mark text by using `ctrl+click`;
simply add the following mousemaps:


```json
[
	{ "button": "button1", "modifiers": ["ctrl"], "command": "text_marker", "press_command": "drag_select" },
	{ "button": "button1", "count": 2, "modifiers": ["ctrl"], "command": "text_marker_clear", "press_command": "drag_select" }
]
```


## Donate

[![Click here to lend your support to TextMarker and make a donation!](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.me/Kronuz/25)


## License

Copyright (C) 2018 German Mendez Bravo (Kronuz). All rights reserved.

MIT license
