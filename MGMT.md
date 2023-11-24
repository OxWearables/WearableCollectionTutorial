Components of the project:
- `autographer.py`: processes camera data  
- omgui movement website: prepares accelerometer for mac
- `wearables.ipynb`: visualise and prepare data

Optionally:
- Camera GUI

# Dependencies
Data collection:
- Python 3.10 
- Google Chrome (possibly homebrew to install it)

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