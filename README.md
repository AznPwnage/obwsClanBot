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


# TODOs
- score gilding
- tracking clan swaps
- track inactivity period (research)

# PATCH NOTES

### v1.1.0
- Added external score editing
- Added saving functionality
- Added inactives view
Minor headsup - regarding saving the score file, it will save on whatever order you have the page currently sorted to, and hence won't preserve the Bungie API ordering (which I can't figure out what it's ordered on)


#### v1.0.4
- Added mod alts to ignore list

#### v1.0.3
- Fixed bug related to inactivity check for Topaz members

#### v1.0.2
- Added an 'All' option in Generate Scores dropdown - this will generate the score sheet for all clans at once. Progress update will be in the cmd window for now.
- Removed the 30 score cap on specialized divisions (onyx/topaz can now achieve +40)
- Added ignore score calculation for Vanguards

#### v1.0.1
- fix width to same as current score in discord view
- color code previous score column in full chart, and flip with score delta
- arial font and light yellowish color for the table cell background fill #FFF2CC
- editable score field (top priority)
- track clan swaps to transfer scores (research)
- allow column selection
- Bold score field in discord view
- Sorting strings take capitals first then lower
- Fix topaz inactive showing class name
- look into getting cross-save name

### v1.0.0
- The generate button will work behind the scenes to generate a score file for that week, so it may take a bit depending on the number of members in the clan.
- Currently only included Thulite's scores from last week, since those're the only ones I've transcribed for testing so far. So other clans will generate scores, but they won't have last week's scores included in them.
- If you click on a clan that doesn't have scores generated for the week, it'll send you to an error page, just hit back or navigate back to 127.0.0.1:5000 and generate the file. This is something I'll handle later on.
- Empire Hunt & Exo Stranger weeklies are currently ambiguous, as they can either be completed, or just not unlocked
