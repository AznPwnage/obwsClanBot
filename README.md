# obwsClanBot
Automation of clan score tracking for OBWS.

Developed and maintained by AznPwnage, for OBWS clan. Any usage of this code in whole or part without the prior knowledge and consent of AznPwnage is not allowed.

# Setup:
Will need to add a key.txt file in your local repo, with the Bungie API key in it, without any whitespace.

### Windows
01. install python3: 
	download at: https://www.python.org/downloads/
	instructions at: https://docs.python.org/3/using/windows.html
02. create a file named "key.txt" within this folder, which contains the Bungie API key
03. from cmd, navigate to this current folder
04. run this command: py -3 -m venv venv
05. run this command: venv\Scripts\activate
06. run this command (only on first install of a new version): pip install flaskr-1.0.0-py3-none-any.whl --force-reinstall
07. run this command: set FLASK_APP=flaskr && set FLASK_ENV=development && flask run
08. You can access the webpage at 127.0.0.1:5000 on your browser

### Packaging command
python setup.py bdist_wheel
