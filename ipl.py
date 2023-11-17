import pandas as pd
import numpy as np

ipl_matches = "IPL_Matches_2008_2022.csv"
matches = pd.read_csv(ipl_matches)

ipl_ball_by_ball = "IPL_Ball_by_Ball_2008_2022.csv"
balls = pd.read_csv(ipl_ball_by_ball)

complete_summary = balls.merge(matches, how='inner', on='ID').copy()


complete_summary['Bowling Team'] = complete_summary['Team1'] + complete_summary['Team2']
complete_summary['Bowling Team'] = complete_summary.apply(lambda x : x['Bowling Team'].replace(x['BattingTeam'], ''), axis=1)
#print(complete_summary)

#batter_data = complete_summary[np.append(balls.columns.values, ['Bowling Team', 'Player_of_Match'])]

def teamsAPI():
    teams = list(set(list(matches['Team1']) + list(matches['Team2'])))
    team_dict = {
        'teams': teams
    }

    return team_dict


def teamvsteamrecordAPI(team1, team2):
    temp_df = matches[((matches['Team1'] == team1) & (matches['Team2'] == team2)) |((matches['Team2'] == team1) & (matches['Team1'] == team2))].copy()

    total_matches = temp_df.shape[0]

    try:
        matches_won_team1 = temp_df[temp_df['WinningTeam'] == team1].shape[0]
    except KeyError:
        matches_won_team1 = 0

    try:
        matches_won_team2 = temp_df[temp_df['WinningTeam'] == team2].shape[0]
    except KeyError:
        matches_won_team2 = 0

    draws = total_matches - (matches_won_team1 + matches_won_team2)

    response = {
        'total_matches': total_matches,
        team1: matches_won_team1,
        team2: matches_won_team2,
        'draws': draws
    }

    return response


def get_team_stats(team_name):
    total_matches= matches[(matches['Team1'] == team_name) | (matches['Team2'] == team_name)].shape[0]
    total_wins= matches[matches['WinningTeam'] == team_name].shape[0]
    total_loss=total_matches-total_wins

    team_stats = {
        'team_name': team_name,
        'total_matches': str(total_matches),
        'total_wins': str(total_wins),
        'total_losses': str(total_loss)
    }
    return team_stats


def get_team_history(team_name):
    team_matches = complete_summary[(complete_summary['BattingTeam'] == team_name) | (complete_summary['Bowling Team'] == team_name)]
    total_matches = team_matches['ID'].nunique()

    total_runs_scored = team_matches['total_run'].sum()
    total_wickets_taken = team_matches[team_matches['player_out'].notnull()].shape[0]
    n_titles = matches[(matches['MatchNumber'] == 'Final') & (matches['WinningTeam'] == team_name)].shape[0]

    response = {
        'team_name':team_name,
        'total_matches': str(total_matches),
        'total_runs_scored': str(total_runs_scored),
        'total_wickets_taken': str(total_wickets_taken),
        'no_of_titles': str(n_titles)
    }
    return response


def get_final_winners_all_seasons(matches_df):

         final_matches = matches_df[matches_df['MatchNumber'] == 'Final']
         final_winners = final_matches[['Season', 'WinningTeam']]

         return final_winners


def get_batsman_record(batsman_name):

    batsman_data = complete_summary[complete_summary['batter'] == batsman_name]


    batsman_stats = batsman_data.groupby('batter').agg(
        total_runs=('batsman_run', 'sum'),
        total_balls_faced=('batsman_run', 'count'),
        total_fours=('batsman_run', lambda x: (x == 4).sum()),
        total_sixes=('batsman_run', lambda x: (x == 6).sum()),
        matches_played=('ID', 'nunique'),
        teams_played_for=('BattingTeam', 'nunique'),
        venues_played_at=('ID', lambda x: matches[matches['ID'].isin(x)]['Venue'].nunique())).reset_index()


    if batsman_stats.empty:
        return {'error': 'No data found for the specified batsman.'}

    batsman_record = {
        'batsman_name': batsman_name,
        'total_runs': str(batsman_stats['total_runs'].iloc[0]),
        'total_balls_faced': str(batsman_stats['total_balls_faced'].iloc[0]),
        'total_fours': str(batsman_stats['total_fours'].iloc[0]),
        'total_sixes': str(batsman_stats['total_sixes'].iloc[0]),
        'matches_played': str(batsman_stats['matches_played'].iloc[0]),
        'teams_played_for': str(batsman_stats['teams_played_for'].iloc[0]),
        'venues_played_at': str(batsman_stats['venues_played_at'].iloc[0])
    }

    return batsman_record


def get_venue_stats(matches_df):
    venue_stats_df = matches_df.groupby('Venue').agg(
        MatchesPlayed=('total_run', 'count'),
        AverageRuns=('total_run', 'mean')
    ).reset_index()


    venue_stats_dict = {
        'Venue': venue_stats_df['Venue'].tolist(),
        'MatchesPlayed': venue_stats_df['MatchesPlayed'].tolist(),
        'AverageRuns': venue_stats_df['AverageRuns'].tolist()
    }

    return venue_stats_dict


def bowler_record(bowler, matches_df):

    matches_df = matches_df[matches_df['bowler'] == bowler]
    innings = matches_df.ID.unique().shape[0]
    nballs = matches_df[~(matches_df.extra_type.isin(['wides', 'noballs']))].shape[0]
    runs = matches_df['batsman_run'].sum()
    if nballs:
        eco = runs / nballs * 6
    else:
        eco = 0
    fours = matches_df[(matches_df.batsman_run == 4) & (matches_df.non_boundary == 0)].shape[0]
    sixes = matches_df[(matches_df.batsman_run == 6) & (matches_df.non_boundary == 0)].shape[0]

    wicket = matches_df.isWicketDelivery.sum()
    if wicket:
        avg = runs / wicket
    else:
        avg = np.inf

    if wicket:
        strike_rate = nballs / wicket * 100
    else:
        strike_rate = np.nan

    gb = matches_df.groupby('ID').sum()
    w3 = gb[(gb.isWicketDelivery >= 3)].shape[0]

    best_wicket = gb.sort_values(['isWicketDelivery', 'batsman_run'], ascending=[False, True])[
        ['isWicketDelivery', 'batsman_run']].head(1).values
    if best_wicket.size > 0:

        best_figure = f'{best_wicket[0][0]}/{best_wicket[0][1]}'
    else:
        best_figure = np.nan
    mo_match = matches_df[matches_df.Player_of_Match == bowler].drop_duplicates('ID', keep='first').shape[0]
    data = {
        'name': bowler,
        'innings': str(innings),
        'wicket': str(wicket),
        'economy': str(eco),
        'average': str(avg),
        'strikeRate': str(strike_rate),
        'fours': str(fours),
        'sixes': str(sixes),
        'best_figure': str(best_figure),
        '3+W': str(w3),
        'mom': str(mo_match)
    }

    return data

def venue_by_sixes(matches_df):
    six_df = matches_df[matches_df['batsman_run'] == 6]
    sixes = six_df.groupby('Venue')['Venue'].count().sort_values(ascending=False)
    return {
        'sixes_by_venue': str(sixes)
    }


def get_team_venue_records(team_name):
        team_records = []
        team_matches = matches[(matches['Team1'] == team_name) | (matches['Team2'] == team_name)]

        for venue in team_matches['Venue'].unique():
            venue_matches = team_matches[team_matches['Venue'] == venue]
            total_matches = venue_matches.shape[0]
            total_wins = venue_matches[venue_matches['WinningTeam'] == team_name].shape[0]
            total_losses = total_matches - total_wins

            venue_record = {
                'total_matches': str(total_matches),
                'total_wins': str(total_wins),
                'total_losses': str(total_losses)

            }
        team_records.append(venue_record)
        return team_records







