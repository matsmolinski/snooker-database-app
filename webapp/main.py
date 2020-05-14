from flask import Flask, Blueprint, request, Response, render_template, url_for, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import date
import requests
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://admin:admin@postgres:5432/default_db'
db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50))
    nationality = db.Column(db.String(30), nullable=False)
    turned_pro = db.Column(db.DateTime, nullable=False)
    highest_break = db.Column(db.Integer, nullable=False)
    ast = db.Column(db.Float)

    def set_ast(self):
        sum = 0
        for x in self.matches_p1:
            sum += x.ast1
        for x in self.matches_p2:
            sum += x.ast2
        if len(self.matches_p1) + len(self.matches_p2) != 0:
            self.ast = sum / (len(self.matches_p1) + len(self.matches_p2))
        else:
            self.ast = 0

    def __repr__(self):
        return '<Player ' + self.first_name + ' ' + self.last_name + ' from ' + self.nationality + '>'

    def __init__(self, first, last, nation, date, hibreak, nickname=None):
        self.id = None
        self.first_name = first
        self.last_name = last
        self.nationality = nation
        self.turned_pro = date
        self.highest_break = hibreak
        self.nickname = nickname


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    date_from = db.Column(db.DateTime)
    date_to = db.Column(db.DateTime)
    venue = db.Column(db.String(30))
    ranked = db.Column(db.Boolean)

    def __repr__(self):
        return '<' + self.name + '>'

    def __init__(self, name, date_from, date_to, venue, ranked):
        self.id = None
        self.name = name
        self.date_from = date_from
        self.date_to = date_to
        self.venue = venue
        self.ranked = ranked


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_one_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    player_two_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournament.id"))
    player_one = db.relationship("Player", foreign_keys="Match.player_one_id", backref="matches_p1")
    player_two = db.relationship("Player", foreign_keys="Match.player_two_id", backref="matches_p2")
    tournament = db.relationship("Tournament", backref="matches")
    score = db.Column(db.String(7))
    winner = db.Column(db.Integer)
    t_round = db.Column(db.String(5))
    ast1 = db.Column(db.Float)
    @db.validates("ast1")
    def update_ast1(self, key, value):
        print(self.player_one)

    ast2 = db.Column(db.Float)
    @db.validates("ast2")
    def update_ast2(self, key, value):
        print(self.player_two)

    def __repr__(self):
        return '< ' + self.player_one.first_name + ' ' + self.player_one.last_name + ' ' + self.score + ' ' + self.player_two.first_name + ' ' + self.player_two.last_name + '>'

    def __init__(self, tournament_id, player_one_id, player_two_id, score, winner, t_round, ast1, ast2):

        self.tournament_id = tournament_id
        self.player_one_id = player_one_id
        self.player_two_id = player_two_id
        self.score = score
        self.winner = winner
        self.t_round = t_round
        self.ast1 = ast1
        self.ast2 = ast2


class Frame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_one_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    player_two_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"))
    player_one = db.relationship("Player", foreign_keys=[
                                 player_one_id], backref="frames_p1")
    player_two = db.relationship("Player", foreign_keys=[
                                 player_two_id], backref="frames_p2")
    match = db.relationship("Match", backref="frames")
    score = db.Column(db.String(7))
    winner = db.Column(db.Integer)

    def __repr__(self):
        return '< ' + self.player_one.first_name + ' ' + self.player_one.last_name + ' ' + self.score + ' ' + self.player_two.first_name + ' ' + self.player_two.last_name + '>'

    def __init__(self, match_id, player_one_id, player_two_id, score, winner):
        self.id = None
        self.match_id = match_id
        self.player_one_id = player_one_id
        self.player_two_id = player_two_id
        self.score = score
        self.winner = winner


class Break(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    author_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    author = db.relationship("Player", backref="breaks")
    frame_id = db.Column(db.Integer, db.ForeignKey("frame.id"))
    frame = db.relationship("Frame", backref="breaks")

    def __repr__(self):
        return '< ' + self.score + ' by ' + self.author.first_name + ' ' + self.author.last_name + '>'

    def __init__(self, score, author_id, frame_id):
        self.id = None
        self.author_id = author_id
        self.frame_id = frame_id
        self.score = score


db.drop_all(bind=None)
db.create_all()

db.session.add(Tournament('Welsh open', date(2020, 2, 10),
                          date(2020, 2, 16), 'Motorpoint Arena', True))
db.session.add(Player('Neil', 'Robertson', 'Australia', date(
    1998, 6, 1), 147, nickname="The Thunder from Down Under"))
db.session.add(Player('Jamie', 'Clarke', 'Welsh', date(2018, 6, 1), 127))
m = Match(1, 1, 2, '4-2', 1, 'L128', 18.1, 28.1)
db.session.add(m)
db.session.commit()
db.session.refresh(m)
print(m.player_one)
#match.player_one.set_ast()
#match.player_two.set_ast()

db.session.add(Frame(1, 1, 2, '20-57', 2))
db.session.add(Frame(1, 1, 2, '68-34', 1))
db.session.add(Frame(1, 1, 2, '31-59', 2))
db.session.add(Frame(1, 1, 2, '89-21', 1))
db.session.add(Frame(1, 1, 2, '63-62', 1))
db.session.add(Frame(1, 1, 2, '79-1', 1))
db.session.add(Break(71, 1, 4))
db.session.add(Break(51, 1, 6))
db.session.commit()


@app.route('/', methods=['GET'])
def get_survey():
    lock = request.cookies.get('lock')
    if lock == '1':
        return redirect(url_for('get_thanks'))
    else:
        return render_template("survey.html")


@app.route('/', methods=['POST'])
def upload_survey():
    lock = request.cookies.get('lock')
    if lock == '1':
        return redirect(url_for('get_thanks'))
    correct = True
    if correct:
        survey = Survey(request.form['question1'], request.form['question2'], request.form['question3'], request.form['question4'], request.form['question5'], request.form['question6'],
                        request.form['question7'], request.form['question8'], request.form['question9'], request.form[
                            'question10'], request.form['question11'], request.form['question12'],
                        request.form['question13'], request.form['question14'], request.form['question15'], request.form[
                            'question16'], request.form['question17'], request.form['question18'],
                        request.form['question19'], request.form['question20'], request.form['question21'], request.form[
                            'question22'], request.form['question23'], request.form['question24'],
                        request.form['question25'], request.form['question26'])
        db.session.add(survey)
        db.session.commit()
        resp = make_response(redirect(url_for('get_thanks')))
        resp.set_cookie('lock', '1')
        return resp  # redirect(url_for('get_thanks'))
    else:
        return render_template("survey.html")


@app.route('/thanks', methods=['GET'])
def get_thanks():
    return render_template("thanks.html")


@app.route('/test', methods=['GET'])
def get_test():
    sth = Match.query.options(db.joinedload('frames'))
    for match in sth:
        print(match, [x for x in match.frames if x.winner == 1])
    return 'ok', 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
