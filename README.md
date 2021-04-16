# obwsClanBot
Automation of clan score tracking for OBWS.
Developed and maintained by AznPwnage, for OBWS clan. Any usage of this code in whole or part without the prior knowledge and consent of AznPwnage is not allowed.

# Setup:
Will need to add a key.txt file in your local repo, with the Bungie API key in it, without any whitespace.

==WINDOWS==
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

==PATCH NOTES==
=v1.0.0=
- The generate button will work behind the scenes to generate a score file for that week, so it may take a bit depending on the number of members in the clan.
- I've currently only included Thulite's scores from last week, since those're the only ones I've transcribed for testing so far. So other clans will generate scores, but they won't have last week's scores included in them.
- If you click on a clan that doesn't have scores generated for the week, it'll send you to an error page, just hit back or navigate back to 127.0.0.1:5000 and generate the file. This is something I'll handle later on.
- Empire Hunt & Exo Stranger weeklies are currently ambiguous, as they can either be completed, or just not unlocked
