Ran into some dependency conflicts that were super annoying to try to solve.

The solution I ended up hitting for this was to do the following

conda create -n foo1 python=3.6 --file newcondaenv.yml
Then inside that environment pip install pip_components.txt to force them outside of the conda dependency resolution