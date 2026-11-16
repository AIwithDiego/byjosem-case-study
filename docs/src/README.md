# Image sources

`cover.html` draws the README cover and the social preview (1280x640) from the demo-data screenshot in `../assets/`.

```bash
CHROME=/path/to/chromium NODE_PATH=/path/to/node_modules node shoot.js "file://$PWD/cover.html" ../assets/cover.png
CHROME=/path/to/chromium NODE_PATH=/path/to/node_modules node shoot.js "file://$PWD/cover.html?social" social-preview.png
```
