from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def fetch_team_players():
    url = "https://competitie.vttl.be/index.php?menu=4&perteam=1&club_id=296&div_id=7893_D"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players_data = []
        players_details = []
        
        # Find all tables with class DBTable_short
        tables = soup.find_all('table', class_='DBTable_short')
        
        # Look for the players table (it should have 'Naam' in its header)
        for table in tables:
            header_row = table.find('tr')
            if header_row and 'Naam' in header_row.text:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 6:  # Make sure we have all columns
                        name_cell = cells[0]
                        name_link = name_cell.find('a')
                        
                        player_data = {
                            'name': name_link.text.strip() if name_link else cells[0].text.strip(),
                            'url': name_link['href'] if name_link else '#',
                            'rank': cells[1].text.strip(),
                            'matches': cells[2].text.strip(),
                            'wins': cells[3].text.strip(),
                            'percentage': cells[4].text.strip(),
                            'value': cells[5].text.strip()
                        }
                        
                        players_data.append(player_data)
                        players_details.append(player_data)
                
                print(f"Found {len(players_data)} players")
                break  # Stop after finding the correct table
        
        return players_data, players_details
    except Exception as e:
        print(f"Error fetching team players: {e}")
        return [], []

def fetch_player_data(player_id="91111"):
    url = "https://competitie.vttl.be/?lang=nl&menu=6&result=1&sel=91111&category=1&show_elo_in_table=0"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: Status code {response.status_code}")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all value_badge divs
        value_badges = soup.find_all('div', class_='value_badge')
        if not value_badges:
            raise Exception("No stats found on page")
        
        # First value_badge contains the win percentage
        percentage_value = value_badges[0].find('span', class_='value')
        if not percentage_value:
            raise Exception("Win percentage not found")
        win_percentage = percentage_value.text.strip().replace(',', '.').replace('%', '').strip()
        
        # Find wins and losses
        wins = None
        losses = None
        for badge in value_badges[1:]:
            value = badge.find('span', class_='value')
            label = badge.find('div', class_='label')
            if not value or not label:
                continue
                
            value_text = value.text.strip()
            label_text = label.text.strip().lower()
            
            if 'gewonnen' in label_text:
                wins = value_text
            elif 'verlies' in label_text or 'verloren' in label_text:
                losses = value_text
        
        if not wins or not losses:
            raise Exception("Wins or losses not found")
        
        # Get summary data
        summary_data = []
        summary_table = soup.find('table', class_='DBTable_short')
        if summary_table:
            rows = summary_table.find_all('tr')[1:]
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    summary_data.append({
                        'name': cells[0].text.strip(),
                        'rank': cells[1].text.strip(),
                        'matches': cells[2].text.strip(),
                        'wins': cells[3].text.strip(),
                        'percentage': cells[4].text.strip(),
                        'value': cells[5].text.strip()
                    })
        
        return "YANNICK DE RYCK", "D6", "0", win_percentage, wins, losses, summary_data

    except Exception as e:
        print(f"Error fetching player data: {e}")
        # Return None values to indicate failure
        return None, None, None, None, None, None, None

def fetch_youth_team_data():
    url = "https://competitie.vttl.be/index.php?menu=4&perteam=1&club_id=296&div_id=8008_A"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        youth_team_data = []
        
        # Find the table with the team standings
        tables = soup.find_all('table', class_='DBTable_short')
        
        for table in tables:
            header_row = table.find('tr')
            if header_row and 'Plaats' in header_row.text:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 8:  # Ensure all columns are present
                        team_data = {
                            'position': cells[0].text.strip(),
                            'team_name': cells[1].find('a').text.strip(),
                            'team_url': cells[1].find('a')['href'],
                            'aw': cells[2].text.strip(),
                            'gw': cells[3].text.strip(),
                            'vw': cells[4].text.strip(),
                            'dw': cells[5].text.strip(),
                            'ff': cells[6].text.strip(),
                            'score': cells[7].text.strip()
                        }
                        youth_team_data.append(team_data)
                
                print(f"Found {len(youth_team_data)} teams")
                break  # Stop after finding the correct table
        
        return youth_team_data
    except Exception as e:
        print(f"Error fetching youth team data: {e}")
        return []

def fetch_youth_team_players():
    url = "https://competitie.vttl.be/index.php?menu=4&perteam=1&club_id=296&div_id=8008_A"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        youth_players_data = []
        
        # Find the table with the player data
        tables = soup.find_all('table', class_='DBTable_short')
        
        for table in tables:
            header_row = table.find('tr')
            if header_row and 'Naam' in header_row.text:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 6:  # Ensure all columns are present
                        player_data = {
                            'name': cells[0].find('a').text.strip(),
                            'url': cells[0].find('a')['href'],
                            'rank': cells[1].text.strip(),
                            'matches': cells[2].text.strip(),
                            'wins': cells[3].text.strip(),
                            'percentage': cells[4].text.strip(),
                            'value': cells[5].text.strip()
                        }
                        youth_players_data.append(player_data)
                
                print(f"Found {len(youth_players_data)} youth players")
                break  # Stop after finding the correct table
        
        return youth_players_data
    except Exception as e:
        print(f"Error fetching youth team players: {e}")
        return []

def fetch_team_standings():
    url = "https://competitie.vttl.be/index.php?menu=4&perteam=1&club_id=296&div_id=7893_D"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        standings_data = []
        
        # Find the standings table
        tables = soup.find_all('table', class_='DBTable_short')
        
        for table in tables:
            header_row = table.find('tr')
            if header_row and 'Plaats' in header_row.text:
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 8:  # Ensure all columns are present
                        team_data = {
                            'position': cells[0].text.strip(),
                            'team_name': cells[1].find('a').text.strip(),
                            'team_url': cells[1].find('a')['href'],
                            'aw': cells[2].text.strip(),
                            'gw': cells[3].text.strip(),
                            'vw': cells[4].text.strip(),
                            'dw': cells[5].text.strip(),
                            'ff': cells[6].text.strip(),
                            'score': cells[7].text.strip()
                        }
                        standings_data.append(team_data)
                break
        
        return standings_data
    except Exception as e:
        print(f"Error fetching team standings: {e}")
        return []

@app.route('/')
def index():
    try:
        standings_data = fetch_team_standings()
        players_data, players_details = fetch_team_players()
        youth_team_data = fetch_youth_team_data()
        youth_players_data = fetch_youth_team_players()
        player_name, player_rank, elo_points, win_percentage, wins, losses, summary_data = fetch_player_data()
        return render_template('index.html', 
                             standings_data=standings_data,
                             players_data=players_data,
                             players_details=players_details,
                             youth_team_data=youth_team_data,
                             youth_players_data=youth_players_data,
                             player_name=player_name,
                             player_rank=player_rank,
                             elo_points=elo_points,
                             win_percentage=win_percentage,
                             wins=wins,
                             losses=losses,
                             summary_data=summary_data)
    except Exception as e:
        print(f"Error: {e}")
        return f"An error occurred: {str(e)}"

@app.route('/update_data')
def update_data():
    try:
        player_name, player_rank, elo_points, win_percentage, wins, losses, summary_data = fetch_player_data()
        
        # If fetch_player_data returned None values, return an error
        if player_name is None:
            return jsonify({'error': 'Failed to fetch new data'}), 500
            
        return jsonify({
            'player_name': player_name,
            'player_rank': player_rank,
            'elo_points': elo_points,
            'win_percentage': win_percentage,
            'wins': wins,
            'losses': losses,
            'summary_data': summary_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)