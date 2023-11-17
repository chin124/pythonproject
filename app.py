from flask import Flask,jsonify,request

import ipl

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Cricket Analyst"


@app.route('/api/teams')
def teams():
    teams = ipl.teamsAPI()
    return jsonify(teams)


@app.route('/api/teamvsteamrecord/<team1>/<team2>', methods=['GET'])
def team_vs_team_record(team1,team2):
    if not team1 or not team2:
        return jsonify({'error': 'Please provide both Team 1 and Team 2'})

    result = ipl.teamvsteamrecordAPI(team1, team2)
    return jsonify(result)

@app.route('/api/teamstats/<team_name>', methods=['GET'])
def team_stats_summary(team_name):
    team_summary = ipl.get_team_stats(team_name)
    return jsonify(team_summary)


@app.route('/api/final_winners', methods=['GET'])
def get_all_final_winners():
    all_final_winners = ipl.get_final_winners_all_seasons(ipl.matches)
    return jsonify(all_final_winners.to_dict(orient='records'))


@app.route('/batsman/<batsman_name>/record', methods=['GET'])
def get_batsman_api(batsman_name):
    batsman_record = ipl.get_batsman_record(batsman_name)
    return jsonify(batsman_record)

@app.route('/api/venue_stats', methods=['GET'])
def venue_stats():
    venue_stats = ipl.get_venue_stats(ipl.complete_summary)
    return jsonify(venue_stats)


@app.route('/api/bowler_record/<bowler>', methods=['GET'])
def api_bowler_record(bowler):
    data = ipl.bowler_record(bowler,ipl.complete_summary)
    return jsonify(data)

@app.route('/api/team_history/<team_name>', methods=['GET'])
def api_team_history(team_name):
    data = ipl.get_team_history(team_name)
    return jsonify(data)

@app.route('/api/sixes_by_venue', methods=['GET'])
def api_six_by_venue():
    data = ipl.venue_by_sixes(ipl.complete_summary)
    return jsonify(data)

@app.route('/api/teamvenuerecords/<team_name>', methods=['GET'])
def team_venue_records(team_name):
    team_venue_records = ipl.get_team_venue_records(team_name)
    return jsonify(team_venue_records)





if __name__ == '__main__':
    app.run(debug=True)