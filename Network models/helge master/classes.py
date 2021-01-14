import numpy as np
import random
from parameters import *

class Person:

    def __init__(self, id_number, age, **kwargs):
        self.id_number = id_number
        self.age = age

        self.decade = min(age-age%10, 80)
        self.inNursing = False
        
        self.state = 'S'
        self.quarantine = False
        self.sick = False
        self.relInfectivity = 0.0
        
        self.infAnc = -1
        self.infDesc = []
        self.cliques = []

        self.present = {}
        for layer in layers:
            self.present[layer] = True

        if age < 19:
            self.ageGroup = 'B'
        elif age < 55:
            self.ageGroup = 'A1'
        elif age < 65:
            self.ageGroup = 'A2'
        elif age < 80:
            self.ageGroup = 'E1'
        else:
            self.ageGroup = 'E2'


    def __repr__(self):
        return 'ID:{:2}, state: {}, age: {:2}, cliques: {}'.format(self.id_number, self.state, self.age, self.cliques)


    def infectNode(self, anc, layer, day):
        self.state = 'E'
        self.lastDay = day
        self.nextDay = day+1+np.random.poisson(dur['I-E'])
        self.infAnc = [anc, layer]
        anc.infDesc.append([self, layer])


    def generateActivity(self, params):
        if self.age in ['A1, A2', 'E1']:
            self.activity = int(max(np.random.normal(params['mode'], params['var']), 1) + pow(random.random(), params['exp']))
        else:
            self.activity = int(max(np.random.normal(params['mode'], params['var']), 1))
            

    # Testing and quarantine functions

    def test(self, fpr=0, fnr=0):
        return self.state in {'Ip', 'Ia','Is'}


    # def test(self, fpr=0, fnr=0):
    #     if self.state in {'Ip', 'Ia'}:
    #         #if (attrs[node]['lastDay'] < day-1):
    #         return random.random() > fnr
    #         #else:
    #         #    return random.random() < fpr
    #     elif self.state == 'Is':
    #         return random.random() > fnr        
    #     else:
    #         return random.random() < fpr


    def quarantineNode(self):
        for layer in {'W', 'US', 'VS', 'BS', 'BH', 'R'}:
            self.present[layer] = False 
        self.quarantine = True
    

    def dequarantineNode(self):
        for layer in {'W', 'US', 'VS', 'BS', 'BH', 'R'}:
            self.present[layer] = True 
        self.quarantine = False


    def individualTestAndQuarantine(self, layers, day):
        if self.test():
            if self.inNursing == False:
                for clique in self.cliques:
                    if clique.name == 'HH':
                        # hhID = clique[1]
                        clique.quarantineClique()


    # State change functions
    def recover(self, params, day):
        self.state = 'R'
        self.lastDay = day
        self.sick = False
        
        for clique in self.cliques:
            clique.cases -= 1

        for layer in self.present:
            self.present[layer] = True
            
        if random.random() < params['NI']:
            self.nextState = 'S'

    def stateFunction(self):
        funcs = {
            'E': self.incubate,
            'Ia': self.asymptomatic,
            'Ip': self.preSymptomatic,
            'Is': self.symptomatic,
            'H': self.hospital,
            'ICU': self.ICU
        }
        return funcs[self.state]
    
    #Daily state progress check and branching functions
    def incubate(self, p, day):
        if day == self.nextDay:
            if random.random() < p['S'][self.decade]:
                self.turnPresymp(p, day)
            else:
                self.turnAsymp(p, day)
        
    def asymptomatic(self, p, day):
        if day == self.nextDay:
            self.recover(p, day)
        

    def preSymptomatic(self, p, day):
        if day == self.nextDay:
            self.activateSymptoms(p, day)
            

    def symptomatic(self, p, day):
        if day == self.nextDay:
            if self.nextState == 'D':
                self.die(p, day)
            elif self.nextState == 'H':
                self.hospitalize(p, day)
            else:
                self.recover(p, day)


    def hospital(self, p, day):
        if day == self.nextDay:
            if self.nextState == 'ICU':
                self.enterICU(p, day)
            elif self.nextState == 'R':
                self.recover(p, day)
            elif self.nextState == 'D':
                self.die(p, day)


    def ICU(self, p, day):
        if day == self.nextDay:
            if self.nextState == 'D':
                self.die(p, day)
            elif self.nextState == 'R':
                self.recover(p, day)

                
    #State change functions
    def recover(self, p, day):
        self.state = 'R'
        self.lastDay = day
        self.sick = False

        for clique in self.cliques:
            clique.cases -= 1
        
        for layer in self.present:
            self.present[layer] = True
            
        if random.random() < p['NI']:
            self.nextState = 'S'

            
    def turnAsymp(self, p, day):
        self.state = 'Ia'
        self.nextState = 'R'
        self.nextDay = day+1+np.random.poisson(dur['AS-R'])
        self.sick = True

        for clique in self.cliques:
            clique.cases += 1
        
        self.relInfectivity = 0.3

    
    def turnPresymp(self, p, day):
        self.state = 'Ip'
        self.nextState = 'Is'
        self.nextDay = day+1+np.random.poisson(dur['PS-I'])
        self.sick = True
        for clique in self.cliques:
            clique.cases += 1
        self.relInfectivity = 3.0
        if self.age < 13:
            self.relInfectivity = 0.3

    
    def activateSymptoms(self, p, day):
        self.state = 'Is'
        self.lastDay = day
        for layer in ['BH', 'BS', 'US', 'VS', 'W', 'NH', 'R']:
            self.present[layer] = False

        if self.inNursing:
            if random.random() < p['NHDage'][self.decade]:
                self.nextState = 'D'
                self.nextDay = day+1+np.random.poisson(dur['I-D'])
            else:
                self.nextState = 'R'
                self.nextDay = day+1+np.random.poisson(dur['I-R'])
                
        elif random.random() < p['HRage'][self.decade]:
            self.nextState = 'H'
            self.nextDay = day+1+np.random.poisson(dur['I-H'])
        else:
            self.nextState = 'R'
            self.nextDay = day+1+np.random.poisson(dur['I-R'])
        self.relInfectivity = 1
        if self.age < 13:
            self.relInfectivity = 0.3

        
    def hospitalize(self, p, day):
        self.state = 'H'
        self.lastDay = day
        for layer in ['HH', 'NH']:
            self.present[layer] = False 

        if random.random() < p['ICUage'][self.decade]:
            self.nextDay = day+1+np.random.poisson(dur['H-ICU'])
            self.nextState = 'ICU'
            
        elif random.random() < p['DRage'][self.decade]:
            self.nextDay = day+1+np.random.poisson(dur['H-D'])
            self.nextState = 'D'
        else:
            self.nextDay = day+1+np.random.poisson(dur['H-R'])
            self.nextState = 'R'

    
    def enterICU(self, p, day):
        self.state = 'ICU'
        self.lastDay = day

        if random.random() < p['DRage'][self.decade]:
            self.nextDay = day+1+np.random.poisson(dur['ICU-D'])
            self.nextState = 'D'
        else:
            self.nextDay = day+1+np.random.poisson(dur['ICU-R'])
            self.nextState = 'R'

        
    def die(self, p, day):
        self.diedFrom = self.state
        self.state = 'D'
        self.lastDay = day
        self.nextDay = -1
        self.nextState = ''
        self.sick = False
        for clique in self.cliques:
            clique.cases -= 1
        for layer in self.present:
            self.present[layer] = False


    def ifSwitch(self, p, day):
        if self.state == 'E':
            self.incubate(p, day)


# ============================================================
# CLIQUE CLASS 
# ============================================================


class Clique:
    '''Clique class containing Persons'''

    def __init__(self):
        # self.id_number = id_number
        self.nodes = []
        self.open = True
        self.openRating = 1.0
        self.cases = 0


    def __repr__(self):
        return 'Clique: persons: {}, open: {}'.format(len(self.nodes), self.open)

    def __iter__(self):
        return self.nodes.__iter__()

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, key):
        return self.nodes[key]


    def get_size(self):
        return len(self.nodes)


    def hasCases(self):
        '''Check to see whether cliqueday needs to be run or not'''
        for node in self.nodes:
            # if node.state in {'Ip','Is','Ia'}:
            if node.sick:
                return True
        return False


    def pooledTest(self, fpr=0, fnr=0):
        for node in self.nodes:
            if node.test():
                if random.random() < fnr:
                    return False
                else:
                    return True
        return False


    def pooledTestAdultOnly(self, age=18, fpr=0, fnr=0):
        for node in self.nodes:
            if node.age > age and node.test():
                return True
        return False
    

    def quarantineClique(self):
        for node in self.nodes:
            node.quarantineNode()
    

    def dequarantineClique(self):
        for node in self.nodes:
            node.dequarantineNode()


    def testAndQuarantine(self, fpr=0, fnr=0):
        if self.pooledTest():
            self.quarantineClique()
        else:
            self.dequarantineClique()


    def testAndQuarantineAdults(self, age,fpr=0, fnr=0):
        if self.pooledTestAdultOnly(age):
            self.quarantineClique()
        else:
            self.dequarantineClique()


# ============================================================
# LAYER CLASS 
# ============================================================


class Layer:
    '''Layer class containing cliques'''

    def __init__(self, name):
        self.name = name
        self.cliques = []
        self.open = True


    def __repr__(self):
        persons = 0
        for clique in self.cliques:
            persons += clique.get_size()
        return 'Layer: {}, cliques: {}, persons: {}, open: {}'.format(self.name, len(self.cliques), persons, self.open)


    def __iter__(self):
        return self.cliques.__iter__()


    def addClique(self, Clique):
        self.cliques.append(Clique)




# ============================================================
# PARAMETER CLASS 
# ============================================================

# class Parameters:

#     def __init__(self):
#         self.p = 0



def main():
    pass

if __name__ == '__main__':
    main()
