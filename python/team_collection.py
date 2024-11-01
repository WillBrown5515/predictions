import requests
import json

class team_info_collector:
    def __init__(self, supabase, foot_api, odds_api):
        self.supabase = supabase
        self.foot_api = foot_api
        self.odds_api = odds_api

    def update_teams(self):
      
        # Specify the ID of the row you want to update
        row_id = 'all_teams'

        # Set the URL for the Premier League teams endpoint
        urls = [f"https://api.football-data.org/v4/competitions/PL/teams",
                f"https://api.football-data.org/v4/competitions/PD/teams",
                f"https://api.football-data.org/v4/competitions/ELC/teams",
                f"https://api.football-data.org/v4/competitions/SA/teams",
                f"https://api.football-data.org/v4/competitions/BL1/teams",
                f"https://api.football-data.org/v4/competitions/FL1/teams"]

        tables = ['Predictions','la-liga-preds','champ-preds','serieA-preds','bundes-preds','ligue1-preds']

        # Set the headers with the API key
        headers = {
            "X-Auth-Token": self.foot_api
        }

        responses = [None] * 6
        team_name_list = [None] * 6
        response_responses = [None] * 6

        # Create a list for the column names
        columns = []
        for i in range(1,21):
            columns.append(str(i))

        update_data = [None] * 6

        # Make the request to the API
        for link in range(len(urls)):
            responses[link] = requests.get(urls[link], headers=headers)

            # Check if the request was successful
            if responses[link].status_code == 200:
                data = responses[link].json()
                teams = data['teams']  # Get the list of teams

                team_name_list[link] = []

                # Print the names of the teams
                for team in teams:
                    team_name_list[link].append(team['name'])
                team_name_list[link].sort()
            else:
                print(f"Error: {responses.status_code} - {responses.text}")

            # Zip the columns to the team names
            update_data[link] = dict(zip(columns, team_name_list[link]))

            # Update the row in the table 'your_table_name'
            response_responses[link] = self.supabase.table(tables[link]).update(update_data[link]).match({'username': row_id}).execute()

    def last_season_results(self):

        url = f"https://api.football-data.org/v4/competitions/PL/standings?season=2023"

        # Set the headers with the API key
        headers = {
            "X-Auth-Token": self.foot_api
        }

        # Make the request to the API
        response = requests.get(url, headers=headers)

        url = f"https://api.football-data.org/v4/competitions/ELC/standings?season=2023"

        response_2 = requests.get(url, headers=headers)

        places = ['1st', '2nd', '3rd']
        for i in range(4,18):
            places.append(str(i)+'th')

        columns = []
        for i in range(1,21):
            columns.append(str(i))

        data = self.supabase.table('Predictions').select('*').eq('username', 'all_teams_prem').execute()

        mid = data.data

        all_teams = [value for key, value in mid[0].items() if key != 'username']

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            standings = data['standings']

            # Extract team names from the data
            team_list = []            
            for stage_data in standings:
                for team_entry in stage_data['table']:  # Iterate through the teams
                    if len(team_list) < 17:
                        team_name = team_entry['team']['name']  # Extract the team name
                        team_list.append(team_name)
            

            last_finishes = [None] * 20
            for team in range(len(team_list)):
                found = all_teams.index(team_list[team])
                last_finishes[found] = places[(team)]
            
            # Identifies the places where the promoted teams are in the list
            something = [index for index, element in enumerate(last_finishes) if element == None]

            data_2 = response_2.json()
            standings_2 = data_2['standings']

            champ_team_list = []            
            for a in standings_2:
                for team_entry in a['table']:  # Iterate through the teams
                    if len(champ_team_list) < 6:
                        team_name = team_entry['team']['name']  # Extract the team name
                        champ_team_list.append(team_name)
            champ_places = ['1st (Champ)', '2nd (Champ)']

            for team in range(len(champ_places)):
                found = all_teams.index(champ_team_list[team])
                last_finishes[found] = champ_places[team]

            champ_places = ['3rd (Champ)']
            for i in range(3):
                champ_places.append(str(i+4)+'th (Champ)')
            champ_team_list = champ_team_list[2:]
            for place in range(len(champ_places)):
                try:
                    found = all_teams.index(champ_team_list[place])
                    last_finishes[found] = champ_places[place]
                except ValueError:
                    print(f"Value not found in the list")

            # Create a list for the column names
            columns = []
            for i in range(1,21):
                columns.append(str(i))

            # Zip the columns to the team names
            update_data = dict(zip(columns, last_finishes))

            row_id = 'all_teams_prem_last_finish'
            response = self.supabase.table('Predictions').update(update_data).match({'username': row_id}).execute()

        else:
            print(f"Error: {response.status_code} - {response.text}")


    def get_odds(self):
        
        # Betfair API credentials
        username = 'email'
        password = 'password'
        app_key = self.odds_api

        # API endpoint for login
        login_url = 'https://identitysso.betfair.com/api/login'

        # Set the login data
        login_data = {
            "username": username,
            "password": password
        }

        # Make the login request
        response = requests.post(login_url, json=login_data, headers={'X-Application': app_key})
        # print("172", response.text)

        # Check if the login was successful
        if response.status_code == 200:
            print("HERE")
            # session_token = response.json()
            print("H2")
            # print(f"Session Token: {session_token}")
        else:
            print(f"Login failed: {response.status_code}, {response.text}")


        # Betfair endpoint to list competitions
        competitions_url = "https://api.betfair.com/exchange/betting/rest/v1.0/listCompetitions/"

        # Headers for the request
        headers = {
            'X-Application': app_key,
            'X-Authentication': 'x7Czq3i2RV0nLKrEQrEwRql/BncIuAoSiqJmeVUaxt8=',
            'Content-Type': 'application/json'
        }

        # Sending request to get football competitions
        payload = json.dumps({
            "filter": {"eventTypeIds": ["1"]}  # EventTypeId 1 represents football
        })

        response = requests.post(competitions_url, headers=headers, data=payload)

        if response.status_code == 200:
            competitions = response.json()
            for competition in competitions:
                if competition['competition']['name'] == "English Premier League":
                    premier_league_id = competition['competition']['id']
                    print(f"Premier League Competition ID: {premier_league_id}")
        else:
            print(f"Error: {response.status_code}, {response.text}")

        # Betfair endpoint to list market catalogue
        market_catalogue_url = "https://api.betfair.com/exchange/betting/rest/v1.0/listMarketCatalogue/"

        # Payload to get the outright winner market
        payload = json.dumps({
            "filter": {
                "competitionIds": [premier_league_id],  # Use the Premier League ID obtained previously
                "marketTypeCodes": ["OUTRIGHT"]          # Looking for the outright winner market
            },
            "maxResults": 1,                            # Limit results to one market
            "marketProjection": ["MARKET_START_TIME", "RUNNER_DESCRIPTION"]
        })

        response = requests.post(market_catalogue_url, headers=headers, data=payload)
        print(response.status_code)
        print(response.text)

        if response.status_code == 200:
            markets = response.json()
            print("MARKETS", markets)
            if markets:
                print("1", markets[0]['marketId'])
                outright_market_id = markets[0]['marketId']
                print(f"Outright Market ID: {outright_market_id}")
        else:
            print(f"Error: {response.status_code}, {response.text}")

        print("OMD", outright_market_id)
        # Betfair endpoint to list market book
        market_book_url = "https://api.betfair.com/exchange/betting/rest/v1.0/listMarketBook/"

        # Payload to get the market book for the outright winner
        payload = json.dumps({
            "marketIds": [outright_market_id],  # Use the market ID obtained previously
            "priceProjection": {
                "priceData": ["EX_BEST_OFFERS"]  # Get the best available odds
            }
        })

        response = requests.post(market_book_url, headers=headers, data=payload)

        if response.status_code == 200:
            market_book = response.json()
            if market_book:
                for runner in market_book[0]['runners']:
                    print(f"Team: {runner['description']['runnerName']}, Odds: {runner['ex']['availableToBack']}")
        else:
            print(f"Error: {response.status_code}, {response.text}")
