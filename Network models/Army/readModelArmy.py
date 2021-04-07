import copy                         
from pprint import pprint

from ArmyTemplate import armyTemplate

attrs = {}
layers = {'lag': [], 'tropp': {}, 'komp': {}, 'bat': {}, 'brig': {}}

def makeTemplate(template, unit, layers, attrs, callStack):                                                                                        
    if 'lag' in template[unit]['units'].keys():
        if 'cliques' not in layers['tropp']:
            layers['tropp']['cliques'] = []
            layers['tropp']['open'] = True
        clique = []
        for _ in range(template[unit]['units']['lag']):
            tmp = []
            count = len(attrs)
            for node in range(count, count+8):                                                                          
                fillAttrs(node, layers)                                          
                tmp.append(node)
            layers['lag'].append(tmp)
            clique.append(tmp)
        layers['tropp']['cliques'].append({'nodes': [i for lag in clique for i in lag], 'open': True})
        for layer in callStack:                         
            tmp = []
            for lag in clique:
                for node in lag:
                    attrs[node]['cliques'].append(layer)
                    tmp.append(node)
            if layer[0] == 'brig':
                if len(layers[layer[0]]['cliques']) > 0:
                    layers[layer[0]]['cliques'][0]['nodes'].extend([i for lag in clique for i in lag])
                else:
                    layers[layer[0]]['cliques'].append({'nodes': [i for lag in clique for i in lag], 'open': True})
        return clique
    else:                                                                                                           
        newStack = copy.deepcopy(callStack)                                                                         
        level = template[unit]['level']
        if 'cliques' not in layers[level]:
            layers[level]['cliques'] = []
            layers[level]['open'] = True
        newStack.append((level, len(layers[level]['cliques'])-1))                                                              
        tmpLag = []
        for subunit in template[unit]['units']:
            for _ in range(template[unit]['units'][subunit]):                                                       
                lag = makeTemplate(template, subunit, layers, attrs, newStack)
                tmpLag.extend(lag)
        if level == 'komp':
            layers['komp']['cliques'].append({'nodes': [i for lag in tmpLag for i in lag], 'open': True})
        if level == 'bat':
            layers['bat']['cliques'].append({'nodes': [i for lag in tmpLag for i in lag], 'open': True})
    return tmpLag

def fillAttrs(node, layers):
    attrs[node] = {}                                                                                        
    attrs[node]['age'] = 20                                                                                 
    attrs[node]['decade'] = 20                                                                              
    attrs[node]['ageGroup'] = 'A1'                                                                          
    attrs[node]['cliques'] = []                                                                             
    attrs[node]['state'] = 'S'                                                                              
    attrs[node]['quarantine'] = False                                                                       
    attrs[node]['sick'] = False                                                                             
    attrs[node]['inNursing'] = False                                                                        
    attrs[node]['present'] = {}                                                                             
    attrs[node]['cliques'].append(('lag', len(layers['lag'])))  

makeTemplate(armyTemplate, 'brigardenord', layers, attrs, [])

pprint(layers)

