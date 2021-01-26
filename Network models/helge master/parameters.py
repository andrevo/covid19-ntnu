'''
Author: Helge Bergo
Date: January 2021
File: parameters.py

This file contains the global parameters used in the main simulation model. 
'''
import networkx as nx

layers = {'BH': {}, 'BS': {}, 'US': {},
          'VS': {}, 'W': {}, 'HH': {}, 'NH': {}, 'R': {}}

translations = {'Kindergarten': 'BH', 'PrimarySchool': 'BS', 'Household':'HH', 'SecondarySchool': 'US', 
                    'UpperSecondarySchool': 'VS', 'Workplace': 'W', 'NursingHome':'NH'}

# Disease durations
dur = {}
dur['I-E'] = 1

dur['PS-I'] = 5
dur['I-R'] = 5
dur['I-H'] = 6
dur['AS-R'] = 8
dur['H-R'] = 8
dur['H-ICU'] = 4
dur['ICU-R'] = 12
dur['ICU-D'] = dur['ICU-R']
dur['H-D'] = dur['H-ICU']+.5*dur['ICU-D']
dur['I-D'] = dur['I-H']+dur['H-D']


stateList = ['S', 'E', 'Ia', 'Ip', 'Is', 'R', 'H', 'ICU', 'D']
states = ['Susceptible', 'Exposed', 'Asymptomatic ', 'Presymptomatic', 'Symptomatic', 'Recovered', 'Hospitalised', 'ICU', 'Dead']

strat = {'S': 10, 'W': 1, 'R': 1}


#Set base probabilities

baseP = {}
baseP['inf'] = {'BH': 0.00015, 'BS': 0.000015, 'US': 0.00015, 'VS': 0.00015, 'W': 0.00015, 'R': 0.5*pow(10, -6), 'HH': 0.15, 'NH':0.2, 'dynR': 0.0150}
baseP['rec'] = 0.1

#Legg in asymptomatic

baseP['inc'] = 1

#Chance to develop symptoms
baseP['S'] = {0: 0.5, 10: 0.5, 20: 0.5, 30:0.5, 40:0.5, 50: 0.5, 60: 0.5, 70: 0.5, 80: 0.5}

#Chance to hospitalize
baseP['H'] = {'B': 0.0001, 'A1': 0.02, 'A2':0.08, 'E1':0.15, 'E2': 0.184}

#Chance to die once hospitalized
baseP['D'] = {'B': 0.1, 'A1': 0.05, 'A2':0.15, 'E1':0.3, 'E2': 0.40 }
baseP['ICU'] = 0.3
baseP['NI'] = 0


baseP['infRatio'] = {'B': 0.25, 'A1': 1, 'A2': 1, 'E1': 1, 'E2': 1}

#Hospitalization by age bracket
baseP['Hage'] = {0: 0.0001, 10: 0.00048, 20: 0.0104, 30: 0.0343, 40: 0.0425, 50: 0.0816, 60: 0.118, 70: 0.166, 80: 0.184}

#Hospitalization corrected for asymptomatic cases
baseP['HRage'] = {}
for ageGrp in baseP['Hage']:
    baseP['HRage'][ageGrp] = baseP['Hage'][ageGrp]/baseP['S'][ageGrp]

#ICU per hospitalization by age bracket
baseP['ICUage'] = {0: 0.3, 10: 0.3, 20: 0.3, 30: 0.3, 40: 0.3, 50: 0.3, 60: 0.3, 70: 0.3, 80: 0.3}

#HDeath per case by age bracket
baseP['Dage'] = {0: 1.61*pow(10, -5), 10: 6.95*pow(10, -5), 20: 3.09*pow(10, -4), 30: 8.44*pow(10, -4), 40: 1.61*pow(10, -3), 50: 5.95*pow(10, -3), 60: 0.0193, 70: 0.0428, 80: 0.078}



#Death rate by age group
baseP['DRage'] = {}
for ageGrp in baseP['Hage']:
    baseP['DRage'][ageGrp] = baseP['Dage'][ageGrp]/(baseP['Hage'][ageGrp])

    
baseP['NHDage'] = {60: baseP['DRage'][60], 70: baseP['DRage'][70], 80: baseP['DRage'][80]}


stateInf = {}

dur = {}
dur['I-E'] = 5

dur['PS-I'] = 2
dur['I-R'] = 5
dur['I-H'] = 6
dur['AS-R'] = 8
dur['H-R'] = 8
dur['H-ICU'] = 4
dur['ICU-R'] = 12
dur['ICU-D'] = dur['ICU-R']
dur['H-D'] = dur['H-ICU']+.5*dur['ICU-D']
dur['I-D'] = dur['I-H']+dur['H-D']




class Parameters:

    def __init__(self, infected=100, cityName='Trondheim', runDays=50, **kwargs):
        self.n = infected
        self.cityName = cityName
        self.startDay = 0
        self.runDays = runDays

        self.activity = kwargs.get('activity', {'mode':10, 'var':3, 'exp':-0.75})
        self.strategy = kwargs.get('strategy', {'S': 12, 'W': 1, 'R': 1})
        self.testing = kwargs.get('testing', {})
        # self.fpr = kwargs.get('fpr', 0)
        # self.fnr = kwargs.get('fnr', 0)

        self.saveResults = kwargs.get('saveResults', True)
        self.printResults = kwargs.get('printResults', True)
        self.createNetwork = kwargs.get('createNetwork', True)
        
        self.inVec = kwargs.get('inVec',{})

        self.kwargs = kwargs
        
        if self.createNetwork:
            self.tree = nx.DiGraph()


    def __repr__(self):
        return '{}: {} days, {} infected.'.format(self.cityName, self.days[1], self.n)

