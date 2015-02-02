import pandas as pd
import numpy as np

def map_responses_to_net_formatted_values(responses,responses_transformed):
	responses['net_formatted_value'] = np.nan
	if 'question_type' in responses.columns:
		#Map NFVs
		map_7pt_SA_to_net = {7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
		map_10pt_SA_to_net = {10:-1,9:-1,8:-1,7:-1,6:-1,5:-1,4:0,3:0,2:1,1:1}
		map_7pt_7_SA_to_net = {7:1,6:1,5:0,4:-1,3:-1,2:-1,1:-1}
		map_11pt_NPS_1_SA_to_net = {11:-1,10:-1,9:-1,8:-1,7:-1,6:-1,5:-1,4:0,3:0,2:1,1:1}
		map_11pt_NPS_11_SA_to_net = {1:-1,2:-1,3:-1,4:-1,5:-1,6:-1,7:-1,8:0,9:0,10:1,11:1}
		map_10pt_NPS_10_SA_to_net = {10:1,9:1,8:0,7:0,6:-1,5:-1,4:-1,3:-1,2:-1,1:-1}
		map_zero_scale_11pt_NPS_to_net = {0:-1,1:-1,2:-1,3:-1,4:-1,5:-1,6:-1,7:0,8:0,9:1,10:1}
		if responses_transformed:
			map_7pt_SA_to_net = {(8-k):v for (k,v) in map_7pt_SA_to_net.items()}
			map_10pt_SA_to_net = {(11-k):v for (k,v) in map_10pt_SA_to_net.items()}
			map_11pt_NPS_1_SA_to_net = {(12-k):v for (k,v) in map_11pt_NPS_1_SA_to_net.items()}

			#Map NFVs
			responses.ix[responses.question_type == '7pt_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_1=SA','response'].map(map_7pt_SA_to_net)
			responses.ix[responses.question_type == '10pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_1=SA','response'].map(map_10pt_SA_to_net)
			responses.ix[responses.question_type == '7pt_7=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_7=SA','response'].map(map_7pt_7_SA_to_net)
			responses.ix[responses.question_type == '11pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '11pt_NPS_1=SA','response'].map(map_zero_scale_11pt_NPS_to_net)
			responses.ix[responses.question_type == '11pt_NPS_11=SA','net_formatted_value'] = responses.ix[responses.question_type == '11pt_NPS_11=SA','response'].map(map_zero_scale_11pt_NPS_to_net)
			responses.ix[responses.question_type == '10pt_NPS_10=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_10=SA','response'].map(map_10pt_NPS_10_SA_to_net)
	
		else:
			#Map NFVs
			responses.ix[responses.question_type == '7pt_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_1=SA','response'].map(map_7pt_SA_to_net)
			responses.ix[responses.question_type == '10pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_1=SA','response'].map(map_10pt_SA_to_net)
			responses.ix[responses.question_type == '7pt_7=SA','net_formatted_value'] = responses.ix[responses.question_type == '7pt_7=SA','response'].map(map_7pt_7_SA_to_net)
			responses.ix[responses.question_type == '11pt_NPS_1=SA','net_formatted_value'] = responses.ix[responses.question_type == '11pt_NPS_1=SA','response'].map(map_11pt_NPS_1_SA_to_net)
			responses.ix[responses.question_type == '11pt_NPS_11=SA','net_formatted_value'] = responses.ix[responses.question_type == '11pt_NPS_11=SA','response'].map(map_11pt_NPS_11_SA_to_net)
			responses.ix[responses.question_type == '10pt_NPS_10=SA','net_formatted_value'] = responses.ix[responses.question_type == '10pt_NPS_10=SA','response'].map(map_10pt_NPS_10_SA_to_net)
			
			#Map responses
			responses.ix[(responses.question_type == '7pt_1=SA') & (responses.response > 7 ),'response'] = np.nan
			responses.ix[(responses.question_type == '7pt_1=SA'),'response'] = 8 - responses.ix[(responses.question_type == '7pt_1=SA'),'response']
			responses.ix[(responses.question_type == '10pt_NPS_1=SA') & (responses.response > 10 ),'response'] = np.nan
			responses.ix[(responses.question_type == '10pt_NPS_1=SA'),'response'] = 11 - responses.ix[(responses.question_type == '10pt_NPS_1=SA'),'response']
			responses.ix[(responses.question_type == '11pt_NPS_1=SA') & (responses.response > 11 ),'response'] = np.nan
			responses.ix[(responses.question_type == '11pt_NPS_1=SA'),'response'] = 12 - responses.ix[(responses.question_type == '11pt_NPS_1=SA'),'response'] -1
			responses.ix[(responses.question_type == '11pt_NPS_11=SA'),'response'] = responses.ix[(responses.question_type == '11pt_NPS_11=SA'),'response'] -1
			responses.ix[(responses.question_type == '11pt_NPS_11=SA') & (responses.response > 11 ),'response'] = np.nan
			responses.ix[(responses.question_type == '7pt_7=SA') & (responses.response > 7 ),'response'] = np.nan
			responses.ix[(responses.question_type == '10pt_NPS_10=SA') & (responses.response > 10 ),'response'] = np.nan

	else:
		map_7pt_SA_to_net = {8:None,7:-1,6:-1,5:-1,4:-1,3:0,2:1,1:1}
		responses['net_formatted_value'] = responses.response.map(map_7pt_SA_to_net)
	return responses