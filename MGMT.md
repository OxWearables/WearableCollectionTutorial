# Components of the project
Data processing:
- omgui movement website: prepares accelerometer for mac
- other application for windows...

Scripts:
- `annotate.py`: annotate image data in a notebook,
- `autographer.py`: processes camera data,
- `sensorplot.py`: plot sensor data from accelerometer and images on same plot.

Practicals
- `prac1-sensor-setup.md`: instructions for data-collection using autographers and axivity's
- `prac2-data-annotation.ipynb`: processing, visualising, and annotating authographer and axivity data

Optionally:
- (Camera GUI)

# Dependencies
Data collection:
- Python 3.10 
- Google Chrome (possibly homebrew to install it)

Running notebooks:
- notebook

Data processing:
- Python 3.10
- actipy (requires java, we suggest using homebrew to install this)
- numpy
- matplotlib
- pillow


## Actipy: for processing accelerometer data
Set up a virtual environment with python 3.10 (tested).

To install java for actipy on the iMacs, use homebrew:
```shell
brew install java
```

And then, follow the suggestion from homebrew and run:
```shell
sudo ln -sfn /opt/homebrew/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
``` 