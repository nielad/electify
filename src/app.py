import streamlit as st 
import pandas as pd
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
import ast
import math

st.set_page_config(page_title="Electify", page_icon="images/favicon.webp")

df_2024 = pd.read_csv("other_data/presidential predict data 2024.csv")
df_train = pd.read_csv("other_data/presidential election training data 2000-2020.csv")
df_paths_to_victory = pd.read_csv("other_data/paths_to_victory.csv")

df_train.set_index('state_year', inplace=True)
df_2024.set_index('state_year', inplace=True)
state_poll_dict = df_2024['dem_poll_advantage'].to_dict()
state_poll_dict = {key.split("_")[0]: value for key, value in state_poll_dict.items()}


st.image('images/android-chrome-192x192.png')

st.write("""
# Electify
## 2024 Presidential Election Forecasting

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

st.write(""" ### State Probabilities""")
st.write("Open the sidebar and adjust the polling spread sliders to see how the odds are impacted")
st.write("The default values of the slider are real time polling average by state.")

 

df_2024_predictions_display = df_2024_predictions.applymap(to_percent_up)

st.dataframe(df_2024_predictions_display)

trump_paths = ast.literal_eval(df_paths_to_victory[df_paths_to_victory['candidate'] == 'Trump']['paths_to_victory'].iloc[0])
trump_probs = df_2024_predictions['trump']
biden_paths = ast.literal_eval(df_paths_to_victory[df_paths_to_victory['candidate'] == 'Biden']['paths_to_victory'].iloc[0])
biden_probs = df_2024_predictions['biden']

st.write(""" ### Total chances of winning""")

st.write("Trump probability of winning: " + str(to_percent_up(find_total_prob_of_winning(trump_paths, trump_probs))))
st.write("Biden probability of winning: " + str(to_percent_up(find_total_prob_of_winning(biden_paths, biden_probs))))

def create_faq(question, answer):

    with st.expander(question):
        st.write(answer)
        
    return
def create_faq_link(question, answer, link, link_label, formula):

    with st.expander(question):
        st.write(answer)
        if formula != "":
            st.latex(r'''
            \text{Probablity (Winning path to victory) =} \newline
            P(A \cap B \cap \neg C) = P(A) \times P(B) \times (1- P(C))\newline \newline \newline
            \text{Probability(Winning the election) = }\newline
            \sum_{i=1}^{n} a_i \newline
            \text{where } a_i = \text {a path to victory}
            ''')
        if link != "":
            st.page_link(link, label = link_label)
        
        
    return
    
create_faq_link("How does the model work?", """
            The model uses a machine learning method called Random Forest. A gentle, non-math introduction to Random Forest can be found in the link below.

            The more technical explanation is that the  model uses a 80/20 training-test split and has an F1-score of around 90%. 
            To predict the current cycle, the model is refitted with the previous test data
             and predicts each candidate's probability of winning each of the six battleground states. \n  
             US Presidents are chosen by the elctoral college system, and the candidate with 270 electoral college votes
             wins the election. Each candidate has a path to victory and the probability of that path is calculated by the intersection of events formula.              
             The total probability is found by summing the probability of each path to victory.

              """, "https://youtu.be/gkXX4h3qYm4?si=Nm-sTC43Lj1IHKXj", "What is Random Forest? :link:", "formula")

create_faq("What does your model assume?", """
            Each candidate doesn't have the same path to victory. 
            Most states are non-competitive, with some solidly blue or red.  States like North Carolina and Florida, 
            historically Republican and not currently competitive, are excluded from battleground status.
            The model assumes that Biden's safe states give him 221 electoral votes and Trump's safe states give him 235. Thus, Biden has
            fewer paths to victory.
            
            """)

create_faq("What data did you use to train the model?", """
The model is trained on data from 21 competitive states across the past six presidential election cycles (since 2000), 
including factors like race and ethnicity, cost of voting, median income, college education, and day-of-election polling averages. 
""")
  
create_faq("Where are you getting your polling averages?", """
Real Clear Politics
""")

create_faq("What are some other characteristics of the model?", """
The model treats each state-year mapping independently. Arizona in 2004 is handled the same as Wisconsin in 2016. The name of the state and the year is not an x variable. 
In other words, it doesn't track trends of battleground states. It also doesn't forecast uncertainty, though in the future I'll probably
add a monte carlo simulation for polling spread  due to its variablity.  \n

The model distinguishes the outcome as binary: either a Democrat won or didn't win. It doesn't reflect individual candidates or platforms or political philosophies. 
""")

st.write("created by Daniel Foster.")
st.page_link("http://github.com/nielad/electify", label = "Github :link:")