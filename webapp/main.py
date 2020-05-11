from flask import Flask, Blueprint, request, Response, render_template, url_for, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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
    nationality = db.Column(db.Integer, nullable=False)
    turned_pro = db.Column(db.DateTime, nullable=False)
    highest_break = db.Column(db.Float, nullable=False)

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

class Frame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_one_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    player_two_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    player_one = db.relationship("Player", foreign_keys=[player_one_id])
    player_two = db.relationship("Player", foreign_keys=[player_two_id])
    score = db.Column(db.String(7))
    winner = db.Column(db.Integer)
    
    def __repr__(self):
        return '< ' + self.player_one.first_name + ' ' + self.player_one.last_name + ' ' + self.score + ' ' + self.player_two.first_name + ' ' + self.player_two.last_name +'>'

    def __init__(self, player_one_id, player_two_id, score, ):
        self.id = None
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
        return '< ' + self.score + ' by '+ self.author.first_name + ' ' + self.author.last_name + '>'

    def __init__(self, score, author_id, frame_id):
        self.id = None
        self.author_id = author_id
        self.frame_id = frame_id
        self.score = score


db.create_all()


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)