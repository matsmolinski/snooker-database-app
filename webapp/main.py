from flask import Flask, Blueprint, request, Response, render_template, url_for, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import date
import requests
import json
import copy


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

    def set_highbreak(self):
        for brk in self.breaks:
            print(brk.score)
            if brk.score > self.highest_break:
                self.highest_break = brk.score

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
    player_one = db.relationship(
        "Player", foreign_keys="Match.player_one_id", backref="matches_p1")
    player_two = db.relationship(
        "Player", foreign_keys="Match.player_two_id", backref="matches_p2")
    tournament = db.relationship("Tournament", backref="matches")
    score = db.Column(db.String(7))
    winner = db.Column(db.Integer)
    t_round = db.Column(db.String(5))
    ast1 = db.Column(db.Float)
    ast2 = db.Column(db.Float)

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
m.player_one.set_ast()
m.player_two.set_ast()

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
def get_interface():
    return render_template("mainpage.html")


@app.route('/test', methods=['GET'])
def get_test():
    sth = Match.query
    for match in sth:
        print(match, [x for x in match.frames if x.winner == 1])
    return 'ok', 200


@app.route('/player', methods=['GET'])
def add_player_template():
    return render_template("addplayer.html")


@app.route('/player', methods=['POST'])
def add_player():
    player = Player(request.form.get("firstname"), request.form.get("lastname"), request.form.get(
        "nationality"), request.form.get("date"), request.form.get("highbreak"), request.form.get("nickname"))
    db.session.add(player)
    db.session.commit()
    return render_template("addplayer.html")

@app.route('/player/<id>', methods=['GET'])
def get_player(id):
    player = Player.query.get(id)
    return render_template("player.html", player=player, year=player.turned_pro.year)

@app.route('/player/<id>/edit', methods=['GET'])
def edit_player(id):
    player = Player.query.get(id)
    month = ('0' if player.turned_pro.month < 10 else '') + str(player.turned_pro.month)
    day = ('0' if player.turned_pro.day < 10 else '') + str(player.turned_pro.day)
    datee = str(player.turned_pro.year) + '-' + month + '-' + day
    print(datee)
    return render_template("editplayer.html", player=player, turned_pro=datee)

@app.route('/player/<id>/edit', methods=['POST'])
def update_player(id):
    player = Player.query.filter_by(id=id).update(dict(first_name=request.form.get("firstname"),last_name=request.form.get("lastname"), nationality=request.form.get("nationality"),turned_pro=request.form.get("date"), highest_break=request.form.get("highbreak"), nickname=request.form.get("nickname")))
    db.session.commit()
    return redirect(url_for('get_player', id=id))

@app.route('/tournament', methods=['GET'])
def add_tournament_template():
    return render_template("addtournament.html")


@app.route('/tournament', methods=['POST'])
def add_tournament():
    tournament = Tournament(request.form.get("name"), request.form.get("datefrom"), request.form.get(
        "dateto"), request.form.get("venue"), not request.form.get("ranked") == None)
    db.session.add(tournament)
    db.session.commit()
    return render_template("addtournament.html")


@app.route('/match', methods=['GET'])
def add_match_template():
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    return render_template("addmatch.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years)


@app.route('/match', methods=['POST'])
def add_match():
    scores = request.form.get('score').split("-")
    match = Match(request.form.get('idt'), request.form.get('id1'), request.form.get('id2'), request.form.get(
        'score'), 1 if scores[0] > scores[1] else 2, request.form.get('round'), request.form.get('ast1'), request.form.get('ast2'))
    db.session.add(match)
    db.session.commit()
    db.session.refresh(match)
    match.player_one.set_ast()
    match.player_two.set_ast()
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    for i in range(0, int(scores[0]) + int(scores[1])):
        breaks_p1 = request.form.get(str(i) + " b1").replace(" ", "").split(",")
        breaks_p2 = request.form.get(str(i) + " b2").replace(" ", "").split(",")
        score_p1 = request.form.get(str(i) + " s1")
        score_p2 = request.form.get(str(i) + " s2")
        winner = 1 if int(score_p1) > int(score_p2) else 2
        score = score_p1 + "-" + score_p2
        frame = Frame(match.id, request.form.get('id1'), request.form.get('id2'), score, winner)
        db.session.add(frame)
        db.session.commit()
        db.session.refresh(frame)
        for brk in breaks_p1:
            if brk != '':
                db.session.add(Break(int(brk),request.form.get('id1'), frame.id))
        for brk in breaks_p2:
            if brk != '':
                db.session.add(Break(int(brk),request.form.get('id2'), frame.id))   
        db.session.commit()
    db.session.refresh(match)
    match.player_one.set_highbreak()
    match.player_two.set_highbreak()
    db.session.commit()
    return render_template("addmatch.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years)

@app.route('/stats', methods=['GET'])
def stats_template():
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    return render_template("stats.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years, answer=None)

@app.route('/stats/frame-efficiency', methods=['POST'])
def stats_frame_efficiency():
    player = Player.query.get(int(request.form.get('player')))
    win = 0
    all = 0
    for frame in player.frames_p1:
        all = all + 1
        if frame.winner == 1:
            win = win + 1
    for frame in player.frames_p2:
        all = all + 1
        if frame.winner == 2:
            win = win + 1
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    if all > 0:
        answer = "" + str(round(win/all, 4) * 100) + "% (" + str(win) + "/" + str(all) + ")"
    else:
        answer = "No records found"
    return render_template("stats.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years, answer=answer)

@app.route('/stats/century-rate', methods=['POST'])
def stats_century_rate():
    player = Player.query.get(int(request.form.get('player')))
    frames = len(player.frames_p1) + len(player.frames_p2)
    centuries = sum(1 if brk.score >= 100 else 0 for brk in player.breaks)
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    if frames > 0:
        answer = "" + str(round(centuries/frames, 4) * 100) + "% (" + str(centuries) + "/" + str(frames) + ")"
    else:
        answer = "No records found"
    return render_template("stats.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years, answer=answer)


@app.route('/stats/wins-by-nation', methods=['POST'])
def stats_wins_by_nation():
    players = Player.query.filter_by(nationality=request.form.get('nation'))
    win = 0
    all = 0
    for player in players:
        for match in player.matches_p1:
            all = all + 1
            if match.winner == 1:
                win = win + 1
        for match in player.matches_p2:
            all = all + 1
            if match.winner == 2:
                win = win + 1
    players = Player.query.all()
    tours = Tournament.query.all()
    years = []
    for tour in tours:
        years.append(tour.date_from.year)
    if all > 0:
        answer = "" + str(round(win/all, 4) * 100) + "% (" + str(win) + "/" + str(all) + ")"
    else:
        answer = "No records found"
    return render_template("stats.html", players=players, tournaments=tours, player_length=len(players), tournament_length=len(tours), years=years, answer=answer)

@app.route('/draw', methods=['GET'])
def get_draw_selection():
    tournaments = Tournament.query.all()
    ts = []
    for t in tournaments:
        tr = {}
        tr['id'] = t.id
        tr['name'] = t.name
        tr['year'] = t.date_from.year
        ts.append(tr)

    return render_template("drawselection.html", tournament=ts, tournament_length=len(tournaments))

@app.route('/tournament/<id>', methods=['GET'])
def get_draw(id):
    tournament = Tournament.query.get(id)
    return render_template("bracket.html",year = tournament.date_from.year, tournament=tournament)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)