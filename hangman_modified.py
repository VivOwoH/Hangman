import random

import flask # flask framework, allows python program to be used in web development

from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__) #importing name of place hangman packagae

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db' # setting back-end database for the hangman using back end module SQLAlchemy
db = SQLAlchemy(app)

# Model Record

def random_pk():
    ''' Return a random integer from 10^9 to 10^10 inclusive as primary key '''
    return random.randint(1e9, 1e10) #primary key for record in the database

def random_word():
    '''
    Read the file and store the words ONLY IF the word has more than 10 characters.
    Return a randomly chosen word (capitalized) from the sequence.
    '''
    words = [line.strip() for line in open('words.txt') if len(line) > 10]
    return random.choice(words).upper() # Returns a randomly chosen word from the list (words) in all caps

class Game(db.Model): # sets new game record in database based on the Game's information (player name, word, characters entered), modelling the database
    ''' (TODO: Class description)
    Args:
    :param player (str): name of the player
    '''
    
    # pk (int) = primary key, used to identify record
    # word (str) = the answer word
    # tried (str) = all characters entered, include both correct/incorrect ones
    # player (str) = player name,
    # sets each record in the database with 4 different column
    pk = db.Column(db.Integer, primary_key=True, default=random_pk) # First column of the record is the primary key (integer)
    word = db.Column(db.String(50), default=random_word) # Second column of record is the game's session randomly picked word (string)
    tried = db.Column(db.String(50), default='') # Third column of record contains all the letters entered during the game, both correct and incorrect (string)
    player = db.Column(db.String(50)) # Forth column of record contains player's name entered

    # constructor
    def __init__(self, player): #intilizer method, called automatically whenever an instance is created
        # self: refers to the particular instance
        self.player = player # assigned self player instance with the player name

    #property decorator: defines properties by appending function to the in-built function property
    @property # adds property decorator to functions
    # calls property function with errors function e.g property(errors)
    def errors(self):
        ''' Return the set of incorrect characters attempted as one string '''
        return ''.join(set(self.tried) - set(self.word))

    @property # calls property functions with current function eg. property(current)
    def current(self):
        ''' Return the set of correct characters attempted as one string, unknown characters denoted by underscore_ '''
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        ''' Return score 
        score = B + U + L - E

        :B (Base score) = 100
        :U (Unique character in the word) = 2 per character
        :L (Length of word) = 1 per character
        :E (Wrong characters attempted) = -10 points per incorrect character
        '''
        return 100 + 2*len(set(self.word)) + len(self.word) - 10*len(self.errors)

    # Play

    def try_letter(self, letter):
        ''' Return none, try to concatenate the letter to the string of already tried letters
        
        Condition: 
        Letter concatenated if ongoing game && character does not exist in tried letters
        otherwise do nothing
        '''
        if not self.finished and letter not in self.tried:
            self.tried += letter
            db.session.commit()

    def hint(self, length):
        if length <= 15:
            amount_hint = 3
        elif length > 15:
            amount_hint = 4



    # Game status

    @property
    def won(self):
        ''' Return True if all characters in the word have been guessed, False otherwise '''
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

@app.route('/')
def home(): # home screen
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10]
    return flask.render_template('home.html', games=games)

@app.route('/play') #assigns html url to function
# play button on home screen
def new_game():
    player = flask.request.args.get('player') # getting player's name from the flash (html webserver)
    game = Game(player) # setting game as a list based on the player's name
    db.session.add(game) # adding current game session based on the player's name to the database
    db.session.commit() # committing the game to the database
    return flask.redirect(flask.url_for('play', game_id=game.pk)) # redirecting the user to a new html page (play.html) to play Hangman after game has registered into database

@app.route('/play/<game_id>', methods=['GET', 'POST'])
# sets a new game of hangman with a specific id
def play(game_id):  #actual game itself
    game = Game.query.get_or_404(game_id) #defining game based on game id from

    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper() # Getting letter from the input HTML 'letter' name
        if len(letter) == 1 and letter.isalpha():
            game.try_letter(letter)

    if flask.request.method == 'POST':


    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game)

# Main

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True) # runs on the 0.0.0.0 ip address (local host)

