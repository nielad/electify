import streamlit as st 
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
import ast
import math

df_2024 = pd.read_csv("other_data/presidential predict data 2024.csv")
df_train = pd.read_csv("other_data/presidential election training data 2000-2020.csv")
df_paths_to_victory = pd.read_csv("other_data/paths_to_victory.csv")

df_train.set_index('state_year', inplace=True)
df_2024.set_index('state_year', inplace=True)
state_poll_dict = df_2024['dem_poll_advantage'].to_dict()
state_poll_dict = {key.split("_")[0]: value for key, value in state_poll_dict.items()}

st.write("Succesfully setup CI/CD")
st.write("""
# Electify
## 2024 Election Forecasting

""")


# The slider options variable is a list. The state_spread float needs to be inserted
# a list of integers between -9 and 9, then cast as a string in order to 
# prefix the two sides with "B+" and "T+"
	

def create_state_slider_options(integers_list, state_spread):
	# cast the integers (and float) as a string and replace the minus signs with plus signs 
	# and the corresponding candidate letter
	strings_list = [("B+" + str(num).split("-")[1]) if num < 0 else ("T+" + str(num)) for num in integers_list]
	
	if state_spread > 0:
		strings_list[9] = "0"
	else:
		strings_list[10] = "0"
	
	
	strings_list.insert(0, "Biden")
	strings_list.append("Trump")
	return strings_list
	
def create_state_slider_int_list(state_spread, opts):
	# creates slider range
	integers_list = []
	if opts:
		integers_list = list(range(-9, 10))
	else:
		integers_list = list(range(-10,11))
	
	
	integers_list.append(state_spread)
	integers_list = sorted(integers_list)
	return integers_list


	
def create_slider_params(state):
	state_spread = state_poll_dict[state]
	
	val = ''
	# val will represent the default value when the page is rendered, it needs to correspond to an element in the 
	# integers_list that initializes options...
	if state_spread < 0:
		# removes the negative sign for Trump
		val = 'T+' + str(state_spread).split("-")[1]
	elif state_spread > 0:
		val = 'B+' + str(state_spread)
	
	# ...which is why we flip the state_spread sign,
	state_spread *= -1
	int_list = create_state_slider_int_list(state_spread, opts=True)
	
	options = create_state_slider_options(int_list, state_spread)
	
	return st.sidebar.select_slider(state, options = options, value = val)


	# 
def create_polling_spread_input():
	arizona, georgia, michigan, nevada, pennsylvania, wisconsin = [create_slider_params(state) for state in state_poll_dict.keys()]
	
	# input needs to be converted back to floats before running through model
	return arizona, georgia, michigan, nevada, pennsylvania, wisconsin 

def create_input_mapping(state):
	state_spread = state_poll_dict[state]
	state_spread *= -1
	keys = create_state_slider_int_list(state_spread, opts=True)
	keys = create_state_slider_options(keys, state_spread)
	
	
	int_list = create_state_slider_int_list(state_spread, opts=False)
	float_list = [float(x) for x in int_list]
	mapping = dict(zip(keys, float_list))
	return mapping

def clean_user_input(state_poll_dict, user_input_raw_list):
	x = 0
	user_input_clean_list = []
	for state in state_poll_dict.keys():
		# don't forget to flip the sign again. Biden's sign is positive if he is in the lead, negative if losing
		state_map = create_input_mapping(state)
		user_input_raw = user_input_raw_list[x]
		
		user_input_clean = state_map[user_input_raw]
		x += 1
		user_input_clean_list.append(user_input_clean)
	return user_input_clean_list

def find_total_prob_of_winning(paths, probs):

    outcomes_probabilities = []
    
    for outcome in paths:
        probability = 1
        for state, prob in probs.items():
            if state in outcome:
                probability *= prob
            else:
                probability *= (1 - prob)
        outcomes_probabilities.append(probability)
    
    return sum(outcomes_probabilities)

def to_percent_up(x):
    if isinstance(x, float):
        return f"{math.ceil(x * 100)}%"
    return x
	
@st.cache_resource
def load_model():
	rfc = RandomForestClassifier(n_estimators = 100)
	return rfc
	
st.sidebar.header('Polling Spread')
arizona, georgia, michigan, nevada, pennsylvania, wisconsin = create_polling_spread_input()
user_input_raw_list = [arizona, georgia, michigan, nevada, pennsylvania, wisconsin]


user_input_clean_list =clean_user_input(state_poll_dict, user_input_raw_list)
dem_poll_advantage = [poll * -1 for poll in user_input_clean_list]
df_2024['dem_poll_advantage'] = dem_poll_advantage


X = df_train[df_train.columns[0:8]]
Y = df_train.winner

rfc = load_model()
#rfc = RandomForestClassifier(n_estimators = 100)
rfc.fit(X, Y)

predict_prob= (rfc.predict_proba(df_2024[df_2024.columns[0:8]]))
df_2024_predictions = pd.DataFrame(predict_prob, columns=['biden', 'trump'], index =df_2024.index)
df_2024_predictions.index = df_2024_predictions.index.str.replace('_2024', '')
df_2024_predictions.index.name = ''

st.write(""" ### Probability of winning each state""")

df_2024_predictions_display = df_2024_predictions.applymap(to_percent_up)

st.dataframe(df_2024_predictions_display)


trump_paths = ast.literal_eval(df_paths_to_victory[df_paths_to_victory['candidate'] == 'Trump']['paths_to_victory'].iloc[0])
trump_probs = df_2024_predictions['trump']
biden_paths = ast.literal_eval(df_paths_to_victory[df_paths_to_victory['candidate'] == 'Biden']['paths_to_victory'].iloc[0])
biden_probs = df_2024_predictions['biden']

st.write(""" ### Probability of winning the presidential election""")

st.write("Trump probability of winning: " + str(to_percent_up(find_total_prob_of_winning(trump_paths, trump_probs))))
st.write("Biden probability of winning: " + str(to_percent_up(find_total_prob_of_winning(biden_paths, biden_probs))))
