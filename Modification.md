# Flask-SQL notes
- db.Model is baseclass for all models, stored on the SQLAlchemy instance
- db.Column = define a columnl; 
	- 1st arg = String name
	- primary_key = True means set this data column as the primary key that is used to identify records
- cache issue
	- known problematic datatypes: JSON
	- When checking changes in browser, use developer tool -> Network -> Disable cache, else the changes will not be updated

# Confirmed implemented modification
- Multiple languages
	- skeleton code done
	- languages (English, French, Italian, Spanish and German)

# Ongoing Modification
- Clue feature
- Option to select difficulty
- Fully-fledged + better looking UI
	- Main Menu
	- Pause Overlay
		- restart
		- return to menu
	- Levels? (unsure as can potentially change main game mechanism like scoring)


# Consider to be Modified
- The game only accept words with more than 10 characters
