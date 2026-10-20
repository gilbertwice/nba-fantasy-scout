#!/usr/bin/env python3
"""ESPN public NBA box-score snapshots. No Yahoo authentication or paid API.
Source is unofficial; failure preserves the last valid snapshot and exits nonzero.
"""
import datetime as dt
import json
import os
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'data' / 'players.json'
BASE = 'https://site.api.espn.com/apis/site/v2/sports/basketball/nba'
HEADERS = {'User-Agent': 'NBAFantasyScout/1.0 (public educational dashboard)', 'Accept': 'application/json'}

def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)

def as_int(x):
    try: return int(x)
    except (ValueError, TypeError): return 0

def as_float(x):
    try: return float(x)
    except (ValueError, TypeError): return 0.0

def made_attempted(value):
    try:
        m, a = str(value).split('-', 1)
        return as_int(m), as_int(a)
    except ValueError:
        return 0, 0

def parse_summary(payload, game_id, date):
    output = []
    for team in payload.get('boxscore', {}).get('players', []):
        team_name = team.get('team', {}).get('abbreviation', '')
        for group in team.get('statistics', []):
            labels = [str(x).upper() for x in group.get('labels', [])]
            for entry in group.get('athletes', []):
                athlete = entry.get('athlete', {})
                values = entry.get('stats', [])
                if not values or len(values) != len(labels) or entry.get('didNotPlay'):
                    continue
                d = dict(zip(labels, values))
                minutes = as_float(str(d.get('MIN', '0')).split(':')[0])
                if minutes <= 0: continue
                fgm, fga = made_attempted(d.get('FG', '0-0'))
                ftm, fta = made_attempted(d.get('FT', '0-0'))
                tpm, _ = made_attempted(d.get('3PT', '0-0'))
                ident = str(athlete.get('id', ''))
                name = athlete.get('displayName') or athlete.get('fullName')
                if not ident or not name: continue
                output.append({'id': ident, 'name': name, 'team': team_name, 'date': date, 'gameId': game_id,
                               'min': minutes, 'fgm': fgm, 'fga': fga, 'ftm': ftm, 'fta': fta,
                               'three': tpm, 'pts': as_int(d.get('PTS')), 'reb': as_int(d.get('REB')),
                               'ast': as_int(d.get('AST')), 'stl': as_int(d.get('STL')), 'blk': as_int(d.get('BLK'))})
    return output

def main():
    today = dt.datetime.now(dt.timezone.utc).date()
    days = max(1, min(21, int(os.getenv('SCOUT_DAYS', '10'))))
    games = {}
    scoreboard_ok = 0
    for n in range(days):
        day = today - dt.timedelta(days=n)
        try:
            board = fetch(f'{BASE}/scoreboard?dates={day:%Y%m%d}&limit=100')
            scoreboard_ok += 1
            for event in board.get('events', []):
                state = event.get('status', {}).get('type', {})
                if state.get('completed') or state.get('name') == 'STATUS_FINAL':
                    games[str(event['id'])] = day.isoformat()
        except Exception as exc:
            print(f'WARNING scoreboard {day}: {exc}')
        time.sleep(.12)
    if scoreboard_ok == 0:
        raise RuntimeError('No scoreboard response; preserving previous data')
    rows = []
    summary_ok = 0
    for game_id, date in games.items():
        try:
            stats = parse_summary(fetch(f'{BASE}/summary?event={game_id}'), game_id, date)
            if stats:
                summary_ok += 1
                rows.extend(stats)
        except Exception as exc:
            print(f'WARNING summary {game_id}: {exc}')
        time.sleep(.12)
    if not rows:
        raise RuntimeError('No player box scores; preserving previous data')
    players = {}
    for row in rows:
        p = players.setdefault(row['id'], {'id': row['id'], 'name': row['name'], 'team': row['team'], 'games': 0,
                                             'min': 0, 'fgm': 0, 'fga': 0, 'ftm': 0, 'fta': 0,
                                             'three': 0, 'pts': 0, 'reb': 0, 'ast': 0, 'stl': 0, 'blk': 0})
        p['games'] += 1
        p['team'] = row['team']
        for key in ('min', 'fgm', 'fga', 'ftm', 'fta', 'three', 'pts', 'reb', 'ast', 'stl', 'blk'):
            p[key] += row[key]
    final = []
    for p in players.values():
        g = p['games']
        p['fgPct'] = round(p['fgm'] / p['fga'] * 100, 1) if p['fga'] else None
        p['ftPct'] = round(p['ftm'] / p['fta'] * 100, 1) if p['fta'] else None
        for key in ('min', 'three', 'pts', 'reb', 'ast', 'stl', 'blk'):
            p[key] = round(p[key] / g, 1)
        # Transparent heuristic, not AI or Yahoo add/drop data.
        p['scoutScore'] = round(p['ast'] * 2.2 + p['stl'] * 5 + p['blk'] * 4 + p['three'] * 2 + p['reb'] * .6 + p['pts'] * .2 + min(p['min'], 35) * .12, 1)
        final.append(p)
    final.sort(key=lambda p: (-p['scoutScore'], p['name']))
    output = {'source': 'ESPN public NBA scoreboard/boxscore (unofficial endpoint)',
              'updatedAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'windowDays': days,
              'gamesParsed': summary_ok, 'players': final}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = DEST.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(DEST)
    print(f'Updated {len(final)} players from {summary_ok} games')

if __name__ == '__main__':
    main()
