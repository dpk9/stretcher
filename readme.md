# Stretcher

Software to run the automated DNA stretcher

## How To Run
### Method 1 (Command Prompt)

In a command prompt, type
python stretcher.py {filename}

For example:
```
python stretcher.py sample_recipe.txt
```
### Method 2 (python/ipython terminal)

In a python/ipython console, type

import stretcher
stretcher.runRecipe("{filename}")

For example:
```python
import stretcher
stretcher.runRecipe("sample_recipe.txt")
```

## Recipe Files
Recipe file should simply be a list of functions for Python to read.  Lines
beginning with # will be ignored.  For example:
```python
# This line will be ignored

moveDipDraw(location="A1", dwell_s=20, draw_speed=.3, dip_speed=500)
moveToLoadPosition()
```
This recipe file will move to A1, lower the Z axis at max speed, wait 20
seconds, and raise the Z axis at 300 um/s.  Then it will move to the load
position.