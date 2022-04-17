import random # importing random module; allows production of a random number
# flask framework, allows python program to be used in web development
import flask
import json
# importing a database module, allowing for records of each hangman game 
# to be stored in the back-end
from flask_sqlalchemy import SQLAlchemy
import os, sys

app = flask.Flask(__name__) # importing name of place hangman package

# Database
# setting back-end database for the hangman using back end module SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

hint_max = 3 # maximum amount of hints

# Model Record

def random_pk():
    ''' Return a random integer from 10^9 to 10^10 inclusive as primary key 
    for record in the database '''
    return random.randint(1e9, 1e10)

def random_word():
    '''
    Read the file and store the words ONLY IF the word has more than 10 characters.
    Return a randomly chosen word from the list in all caps.
    '''
    words = [line.strip() for line in open('words.txt') if len(line) > 10]
    return random.choice(words).upper()

def random_word(locale):
    '''
    Overload method, used when localization is provided as parameter
    Locale available: English, French, Italian, Spanish and German
    '''
    filename = "words.txt" # default
    if locale == "fr":
        filename = "words_fr.txt"
    elif locale == "it":
        filename = "words_it.txt"
    elif locale == "es":
        filename = "words_es.txt"
    elif locale == "de":
        filename = "words_de.txt"

    words = [line.strip() for line in open(filename) if len(line) > 10]
    return random.choice(words).upper()

class Game(db.Model):
    ''' blueprint of game records/sessions
    
    Parameter:
    ; db.Model: baseclass for all models, stored on SQLAlchemy instance

    Attributes:
    ; pk (int) = primary key, used to identify record
    ; word (str) = the answer word
    ; tried (str) = all characters entered, include both correct/incorrect ones
    ; player (str) = player name
    ; language(str) = language localization
    '''
    #----------- Class Attributes --------------

    # Each Game record in the database will have 4 columns
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    # Column 1 is the primary key (integer), default assigns the value = random_pk

    word = db.Column(db.String(50), default=random_word)
    # Column 2 is the game's session randomly picked word (string), 
    # default assigns the record value with random word
    
    tried = db.Column(db.String(50), default='')
    # Column 3 contains all the letters entered during the game, 
    # both correct and incorrect (string)
    
    player = db.Column(db.String(50)) 
    # Column 4 contains player's name entered

    language = db.Column(db.String(50), default='en')
    # Column 5 conatins each game session's language setting


    #----------- Class constructor --------------

    # initializer method(constructor), called automatically whenever an instance is created
    def __init__(self, player): 
        # self: refers to the particular instance
        self.player = player # assigned the given parameter to the instance attribute
        self.word = random_word(self.language)
    
    #----------- Properties/Methods --------------

    # property decorator(@property): defines properties by appending function 
    # to the in-built function property

    @property # adds property decorator to functions
    # calls property function with errors function = property(errors)
    def errors(self):
        ''' Return the set of incorrect characters attempted as one string '''
        return ''.join(set(self.tried) - set(self.word))

    @property # calls property functions with current function = property(current)
    def current(self):
        ''' Return the set of correct characters attempted as one string, 
        unknown characters denoted by underscore_ '''
        return ''.join([c if c in self.tried else '_' for c in self.word])

    def hint(self):
        word = self.word # getting generated word
        word = list(word) # splitting letters of word into a list
        letters = []
        for char in word:
            if char not in letters and char not in self.tried: # adding the game word letters to the list 'letters' if they are not tried and are not already in the list
                letters.append(char)
        self.try_letter(letters[0]) # calling the try letter function to input an correct letter into the game

    @property
    def points(self):
        ''' Return score = B + U + L - E

        :B (Base score) = 100
        :U (Unique character in the word) = 2 per character
        :L (Length of word) = 1 per character
        :E (Wrong characters attempted) = -10 points per incorrect character
        '''
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)

    @property
    def locale(self):
        ''' Return localization language chosen for the game session '''
        return self.language

    # Play

    def try_letter(self, letter):
        ''' Return none, try to concatenate the letter 
        to the string of already tried letters
        
        Condition: 
        Letter concatenated if ongoing game && character does not exist in tried letters
        otherwise do nothing
        '''
        if not self.finished and letter not in self.tried:
            self.tried += letter
            db.session.commit()

    ''' TODO: add function description, specify return type '''




    # Game status

    @property
    def won(self):
        ''' Return True if all characters in the word 
        have been guessed, False otherwise '''
        return self.current == self.word

    @property
    def lost(self):
        ''' Return True if reached 6 tries, False otherwise '''
        return len(self.errors) == 6

    @property
    def finished(self):
        ''' Return True if the game is either won/lost, False otherwise '''
        return self.won or self.lost


# Controller

@app.route('/', methods=['GET', 'POST'])  #assigns URL to function
def home(): 
    ''' home page
    Only games that are won are shown in the home page
    Only Top 10 games are shown
    '''
    value = flask.request.form.get('language')
    Game.language = value 

    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10] 
        # get all won game sessions in an array, 
        # sort by descending order of game points,
        # [:10] means obtain first 10 sessions in the sorted array 
    return flask.render_template('home.html', games=games)

# assigns the play.html url to function 
# that will route to the webpage when function is called
@app.route('/play')
def new_game():
    ''' Generating a new game session, and registered into database '''
    player = flask.request.args.get('player') # getting a MultiDict (dictionary object) 
                                    # from the flash (html webserver) with the key being player's name
    game = Game(player) # setting game as a list based on the player's name
    game.language = Game.language

    db.session.add(game) # adding current game session based on the player's name to the database
    db.session.commit() # committing the game to the database
    return flask.redirect(flask.url_for('play', game_id=game.pk)) # redirecting the user to a new html page (play.html) 
                                                                # to play after game has registered into database

# route to play page, url contains unique game session id being the primary key assigned when instantiated
@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    global hint_max
    ''' Main game function '''
    game = Game.query.get_or_404(game_id) # get the game session with game id that is the primary key assigned
    
    # debug | checking language locale of this game session
    print("locale of this game session: " + game.locale)

    # POST is an HTTP request method used to send data from a client to web server to create/update a resource
    if flask.request.method == 'POST':  # if we are sending data to the server
        print('posted')
        print(flask.request.values)
        print(flask.request.form)
        if 'formName' in flask.request.values:
            if flask.request.values['formName'] == 'letter-form': # checking if form letter-form is posted from the HTML
                letter = flask.request.values['letter'].upper()  # Getting letter from the input HTML 'letter' name, capitalized e.g. the input box on the html page
                print(letter)
                if len(letter) == 1 and letter.isalpha():  # Check if one alphabetical character is inputted,
                    game.try_letter(letter)  # call game class with module try_letter, try_letter method if true
            elif flask.request.values['formName'] == 'hint-form': # checking if form hint-form is posted form the HTML
                print('hi')
                if hint_max > 0: # checks if the amount of hint calls is more than 0, more than 0 is if they still have that amount of hint tries left
                    game.hint()
                    hint_max -= 1 # reduce hint call amount
    # XMLHttpRequest(XHR) request object is used to request data from a web server without the need to reload the page
    # *Note: request.is_xhr method has been deprecated since Flask 0.13 and removed in Werkzeug 1.0.0 (unreliable)
    if flask.request.is_xhr:  # if we are requesting data from server
        print(hint_max)
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             hint_max=hint_max,  # send hint_max data to the front-end (HTML)
                             finished=game.finished)  # convert python objects/attributes into json objects
    
    else: # not requesting or sending data
        hint_max = 3  # resetting hint_max when game is concluded
        return flask.render_template('play.html', game=game, hint_max=hint_max) # render html template (based on Jinja2 engine)


# Main
def base_path(path):
    if getattr(sys, 'frozen', None):  # getting attribute of the system if system is frozen
        basedir = sys._MEIPASS  # storing the base directory in a temporary folder called MEIPASS
    else:
        basedir = os.path.dirname(__file__)  # directory path of the file
    return os.path.join(basedir, path)  # concatenates the 2 paths into 1

if __name__ == '__main__':
    os.chdir(base_path(''))
    app.run(debug=True) # runs on the 0.0.0.0 ip address (local host), # also allows debugging tools to be accessed

