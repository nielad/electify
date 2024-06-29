import pandas as pd
import os
import requests
import json
from datetime import datetime
import shutil

print(os.getcwd())
current_date = datetime.now().strftime('%Y-%m-%d')
state = 'North Carolina'

battleground_states = {'Wisconsin' : 'https://www.realclearpolitics.com/poll/race/7398/polling_data.json', 
                       'Pennsylvania' :'https://www.realclearpolitics.com/poll/race/7892/polling_data.json',
                       'Nevada' : 'https://www.realclearpolitics.com/poll/race/7826/polling_data.json',                 
                       'Georgia' : 'https://www.realclearpolitics.com/poll/race/7747/polling_data.json',
                       'Arizona' : 'https://www.realclearpolitics.com/poll/race/7907/polling_data.json',
                       'Michigan' : 'https://www.realclearpolitics.com/poll/race/7953/polling_data.json'}

def download_rcp_files():
    if not os.path.exists('/src/rcp_data'):
        os.makedirs('/src/rcp_data')
    move_old_files()
    # send http request to the RCP json file
    for state, url in battleground_states.items():
        send_http_request(url, state)
def move_old_files():
    directory = '/src/rcp_data'
    old_directory = os.path.join(directory, 'old_polling_data')
    if not os.path.exists(old_directory):
        os.makedirs(old_directory)
        
    # List all files in the directory
    files = os.listdir(directory)

    # Iterate over each file
    for file in files:
        # Check if the file is a .json file
        if file.endswith('.json'):
            # Construct the file path
            file_path = os.path.join(directory, file)
            old_file_path = os.path.join(old_directory, file)
    
            # Move the file to the 'old_polling_data' subdirectory
            shutil.move(file_path, old_file_path)
            print(f"Moved file: {file_path}")
            
def send_http_request(url, state):
    response = requests.get(url)
    # if the response is OK, write the file to the polling data directory
    if response.status_code == 200:
        write_file(state, response)
    else:
        print(f"Failed to download {state} polling data")

def write_file(state, response):
    state_title = f'{state}_polling_data_{current_date}.json'
    filename = os.path.join('rcp_data', state_title)
    with open(filename, 'wb') as file:
        file.write(response.content)
        print(f"Downloaded {state} polling data")


def extract_poll_data():


    # Define the directory where JSON files are stored
    directory = '/src/rcp_data'
    poll_list = []
    
    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            # Construct the full path to the file
            filepath = os.path.join(directory, filename)
            
            # Open the file and process its contents and create the list of dictionaries that contains the data of each file
            poll_dict = open_file(filepath, filename)
            poll_list.append(poll_dict)
    return poll_list

def open_file(filepath, filename):
    with open(filepath, 'r') as file:
        data = json.load(file)
        
        # Process the data as needed
        print(f"Processing {filename}:")
        poll_dict = extract_poll_data_helper(data)
        
        # Extract the state name from the filename
        state_name = filename.split('_')[0]
        poll_dict['state'] = state_name

        poll_dict['date'] = current_date
        return poll_dict
        
def extract_poll_data_helper(data):
# Access the "poll" object
    poll_data = [poll for poll in data['poll'] if poll['type'] == 'rcp_average']
          
    # Extracting the required values
    poll_id = poll_data[0]['id']
    poll_date = poll_data[0]['date']
    second_date = poll_date.split("-")[1].strip()
    trump_value = next(candidate['value'] for candidate in poll_data[0]['candidate'] if candidate['name'] == 'Trump')
    biden_value = next(candidate['value'] for candidate in poll_data[0]['candidate'] if candidate['name'] == 'Biden')
    spread_name = poll_data[0]['spread']['name']
    spread_value = poll_data[0]['spread']['value']
	if spread_value == "":
		spread_value = '+0'
    poll_dict = {'id' : poll_id, 
                 'last_poll_date' : second_date,
                 'trump' : trump_value,
                 'biden' : biden_value,
                 'spread_name' : spread_name,
                 'spread_value' : spread_value.split('+')[1] }
    print(poll_dict)

    return poll_dict



download_rcp_files()
rcp_data = extract_poll_data()

df = pd.DataFrame(rcp_data)
df['dem_poll_advantage'] = df.apply(lambda row: -float(row['spread_value']) if row['spread_name'] == 'Trump' else row['spread_value'], axis=1)

df.to_csv("/src/other_data/daily_state_polling_averages.csv", index = False)
print("Dataframe read to other_data/daily_state_polling_averages.csv")
print(os.getcwd())