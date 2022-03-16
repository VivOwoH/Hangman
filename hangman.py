import random

import flask
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hangman.db'
db = SQLAlchemy(app)

# Model

def random_pk():
    ''' Return a random integer from 10^9 to 10^10 inclusive as primary key '''
    return random.randint(1e9, 1e10)

def random_word():
    '''
    Read the file and store the words ONLY IF the file has more than 10 words.
    Return a randomly chosen word (capitalized) from the sequence.
    '''
    words = [line.strip() for line in open('words2.txt') if len(line) > 10]
    return random.choice(words).upper()

class Game(db.Model):
    ''' (TODO: Class description)
    Args:
    :param player (str): name of the player
    '''
    
    # pk (int) = primary key, used to identify record
    # word (str) = the answer word
    # tried (str) = all characters entered, include both correct/incorrect ones
    # player (str) = player name
    pk = db.Column(db.Integer, primary_key=True, default=random_pk)
    word = db.Column(db.String(50), default=random_word)
    tried = db.Column(db.String(50), default='')
    player = db.Column(db.String(50))

    # constructor
    def __init__(self, player):
        self.player = player

    @property
    def errors(self):
        ''' Return the set of incorrect characters attempted as one string '''
        return ''.join(set(self.tried) - set(self.word))

    @property
    def current(self):
        ''' Return the set of correct characters attempted as one string, unknown characters denoted by underscore_ '''
        return ''.join([c if c in self.tried else '_' for c in self.word])

    @property
    def points(self):
        ''' Return score 
        score = B + U + L - E

        :B (Base score) = 100
        :U (Unique character in the word) = 2/char
        :L (Length of word) = 1/char
        :E (Wrong characters attempted) = -10/char
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
def home():
    games = sorted(
        [game for game in Game.query.all() if game.won],
        key=lambda game: -game.points)[:10]
    return flask.render_template('home.html', games=games)

@app.route('/play')
def new_game():
    player = flask.request.args.get('player')
    game = Game(player)
    db.session.add(game)
    db.session.commit()
    return flask.redirect(flask.url_for('play', game_id=game.pk))

@app.route('/play/<game_id>', methods=['GET', 'POST'])
def play(game_id):
    game = Game.query.get_or_404(game_id)

    if flask.request.method == 'POST':
        letter = flask.request.form['letter'].upper()
        if len(letter) == 1 and letter.isalpha():
            game.try_letter(letter)

    if flask.request.is_xhr:
        return flask.jsonify(current=game.current,
                             errors=game.errors,
                             finished=game.finished)
    else:
        return flask.render_template('play.html', game=game)

# Main

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

