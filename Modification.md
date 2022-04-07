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
- UI change
	- color theme
	- background img

# Modification from testing
- Username limit to <=10 characters

# Ongoing Modification
- Clue feature
- Option to select difficulty

# Consider to be Modified
- The game only accept words with more than 10 characters
