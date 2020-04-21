import random

#Set base probabilities


baseP = {}
baseP['inf'] = {'BH': 0.0002, 'BS': 0.0002, 'US': 0.0002, 'VS': 0.0002, 'W': 0.0002, 'R': 0.5*pow(10, -6), 'HH': 0.1, 'NH':0.01, 'dynR': 0.005}

baseP['rec'] = 0.1

#Legg in asymptomatic

baseP['inc'] = 1

#Chance to develop symptoms
baseP['S' ] = {0: 0.5, 10: 0.5, 20: 0.5, 30:0.5, 40:0.5, 50: 0.5, 60: 0.5, 70: 0.5, 80: 0.5} #Placeholder

#Chance to hospitalize
baseP['H'] = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184}

#Chance to die once hospitalized
baseP['D'] = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 }
baseP['ICU'] = 0.3
baseP['NI'] = 0


baseP['infRatio'] = {'B': 0.25, 'A1': 1, 'A2': 1, 'E1': 1, 'E2': 1}

#Hospitalization by age bracket
baseP['Hage'] = {0: 0.0001, 10: 0.00048, 20: 0.0104, 30: 0.0343, 40: 0.0425, 50: 0.0816, 60: 0.118, 70: 0.166, 80: 0.184}

#ICU per hospitalization by age bracket

baseP['ICUage'] = {0: 0.3, 10: 0.3, 20: 0.3, 30: 0.3, 40: 0.3, 50: 0.3, 60: 0.3, 70: 0.3, 80: 0.3}

#HDeath per case by age bracket
baseP['Dage'] = {0: 1.61*pow(10, -5), 10: 6.95*pow(10, -5), 20: 3.09*pow(10, -4), 30: 8.44*pow(10, -4), 40: 1.61*pow(10, -3), 50: 5.95*pow(10, -3), 60: 0.0193, 70: 0.0428, 80: 0.078}



#Death rate by age group
baseP['DRage'] = {}
for ageGrp in baseP['Hage']:
    baseP['DRage'][ageGrp] = baseP['Dage'][ageGrp]/(baseP['Hage'][ageGrp]*baseP['S'][ageGrp])

baseP['NHDage'] = {60: baseP['Dage'][60], 70: baseP['Dage'][70]}



stateInf = {}




dur = {}
dur['I-E'] = 1
dur['AS-R'] = 8
dur['PS-I'] = 6
dur['I-R'] = 8
dur['I-D'] = 10
dur['I-H'] = 6
dur['H-R'] = 8
dur['H-ICU'] = 6
dur['ICU-R'] = 10
dur['ICU-D'] = 10
