armyTemplate = {}

#Brigarde -> bataljon -> kompani/batteri/Eskadron -> tropp -> lag

armyTemplate['brigardenord'] = {
    'level': 'brig',
    'units' : {
        'telemarkbat' : 1,
        'andrebat' : 1,
        'panserbat' : 1,
        'artilleribat' : 1,
        'ingeniørbat' : 1,
        'sambandsbat' : 1,
        'sanitetsbat' : 1,
        'stridstrenbat' : 1,
        'militærpolitikomp' : 1
        }
}

armyTemplate['telemarkbat'] = {
    'level':'bat',
    'units' : {
        'stridsvogneskadron' : 1,  #Tar med i første omgang, selv om stridsvogner
        'kavalerieskadron' : 1, 
        'mekanisertinfant' : 2,
        'kampstøtteeskadron' : 1
        }
}

armyTemplate['kampstøtteEskadron'] = {
    'level' : 'komp',
    'units' : {
        'eskadronstab' : 1,
        'sambandstropp' : 1,
        'repBergtropp' : 1,
        'bombekastropp' : 1,
        'sanitetstropp': 1
    }
}

armyTemplate['eskadronstab'] = { #ikke tropp, men regner med samme antall lag
    'level' : 'trp',
    'units' : {
            'lag' : 4
    }
}
armyTemplate['sambandstropp'] = {
    'level' : 'trp',
    'units' : {
            'lag' : 4
    }
}

armyTemplate['repBergtropp'] = {
    'level' : 'trp',
    'units' : {
            'lag' : 4
    }
}

armyTemplate['bombekastropp'] = {
    'level' : 'trp',
    'units' :{
            'lag' : 4
    }
}
armyTemplate['sanitetstropp'] = {
    'level' : 'trp',
    'units' :{
            'lag' : 4
    }
}
armyTemplate['lag'] = {
    'level' : 'trp',
    'units' :{
            'lag' : 4
    }
}

armyTemplate['stridsvogneskadron'] = {
    'level' : 'komp',
    'units' : {
        'stridsvognstropp' : 1
    }
}

armyTemplate['stridsvognstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}

armyTemplate['mekanisertinfant'] = {
    'level' : 'komp',
    'units' : {
        'mekanisertinfantstropp' : 1
    }
}

armyTemplate['mekanisertinfantstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}


armyTemplate['andrebat'] = {  #ca 600 menn på kompB, C, kavaleri, støttekomp, betaljonstab
   'level' : 'bat',
   'units' : {
        #'kompA' : 1,  i reserve, ikke i daglig drift
        'kompB' : 1, 
        'kompC' : 1,
        'kavalerieskadron' : 1,
        'støttekomp' : 1,
        'bataljonstab' : 1
    }
}

armyTemplate['kompB'] = {
    'level' : 'komp',
    'units' :{
        'kompBTropp' : 1
    }
}
armyTemplate['kompB'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 15
    }
}

armyTemplate['kompC'] = {
    'level' : 'komp',
    'units' : {
        'kompCTropp' : 1
    }
}
armyTemplate['kompCTropp'] = {
    'level' : 'trp',
    'units' :{
        'lag' : 15
    }
}

armyTemplate['støttekomp'] = {
    'level' : 'komp',
    'units' :{
        'støttekompTropp' : 1
    }
}
armyTemplate['støttekompTropp'] = {
    'level' : 'trp',
    'units' :{
        'lag' : 15
    }
}
armyTemplate['bataljonstab'] = {
    'level' : 'komp',
    'units' :{
        'bataljonstabTropp' : 1
    }
}

armyTemplate['bataljonstabTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 15
    }
}

armyTemplate['kavalerieskadron'] = { #15 lag igjen med 8 per
    'level' : 'komp',
    'units' : {
        'oppklaringstropp' : 1,
        'skarpskyttertropp' : 1,
        'MUAS' : 1
    }
}

armyTemplate['oppklaringstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 5
    }
}

armyTemplate['skarpskyttertropp'] = {
     'level' : 'trp',
    'units' : {
        'lag' : 5
    }
}

armyTemplate['MUAS'] = {
     'level' : 'trp',
    'units' : {
        'lag' : 5
    }
}

armyTemplate['panserbat'] = { #ca 560
    'level' : 'bat',
    'units' : {
        'kavalerieskadron' : 1, #18 lag
        'stridsvogneskadron' : 1, #17 lag
        'stormeskadron' : 2, #35 lag
        'kampstøtteeskadron' : 1 #18 lag
    }
}

armyTemplate['kavalerieskadron']= {  #18
    'level' : 'komp',
    'units' : {
        'oppklaringstropp' : 1,
        'patruljetropp' : 1,
        'sensortropp' : 1
    }
}

armyTemplate['oppklaringstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 6
    }
}
armyTemplate['patruljetropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 6
    }
}

armyTemplate['sensortropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 6
    }
}


armyTemplate['kampstøtteeskadron'] = { #18
    'level' : 'komp',
    'units' : {
        'kommandoplasstropp' : 1,
        'sanitetstropp' : 1,
        'stridstrentropp' : 1,
        'bombekastertropp' : 1
    }
}

armyTemplate['kommandoplasstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}
armyTemplate['sanitetstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 5
    }
}
armyTemplate['stridstrentropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}
armyTemplate['bombekastertropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}

# armyTemplate['strodstrentropp'] = {
#     'forsyningsgruppe' : 1,
#     'reperasjonsgruppe' : 1,
#     'bergningsgruppe' : 1
#     }


# armyTemplate['artilleribat'] = { #ingen/lite info om antall eller tropper nedover
#     'bataljonstab' : 1,
#     'kanonbatteriNOP' : 1,
#     'lokaliseringsbatteri' : 1,
#     'stabsbatteri' : 1,
#     'kampluftvernbatteri' : 1
# }

armyTemplate['ingeniørbataljon'] = { #260 ansatte og 400 vernepliktige
    'level' : 'bat',
    'units' : {
        'Ingeniørkomp' : 1
    }
}
armyTemplate['Ingeniørkomp'] = {
    'level' : 'komp',
    'units' : {
        'Ingeniørtropp' : 1
    }
}
armyTemplate['Ingeniørtropp'] = {
    'level' : 'komp',
    'units' : {
        'lag' : 5
    }
}

armyTemplate['sambandsbat'] = { #ca 600
    'level' : 'bat',
    'units' : {
        'telekomp' : 1,
        'radiokomp' : 1,
        'kommandoplasskomp' : 1
    }
}

armyTemplate['telekomp'] = {
    'level' : 'komp',
    'units' : {
        'teleTropp' : 1
    }
}
armyTemplate['teleTropp'] = {
    'level' : 'komp',
    'units' : {
        'lag' : 25
    }
}

armyTemplate['radiokomp'] = {
    'level' : 'komp',
    'units' : {
        'radioTropp' : 1
    }
}
armyTemplate['radioTropp'] = {
    'level' : 'komp',
    'units' : {
        'lag' : 25
    }
}


armyTemplate['kommandoplasskomp'] = {
    'level' : 'komp',
    'units' : {
        'kommandoplassTropp' : 1
    }
}
armyTemplate['kommandoplassTropp'] = {
    'level' : 'komp',
    'units' : {
        'lag' : 25
    }
}

armyTemplate['sanitetsbat'] = {
    'level' : 'bat',
    'units' : {
        'sykehuskompani' : 1,
        'kompani1Sanitet' : 1,
        'HRS' : 1
    }
}
armyTemplate['sykehuskompani'] = {
    'level' : 'komp',
    'units' : {
        'sykehusTropp' : 1
    }
}

armyTemplate['sykehusTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 9
    }
}

armyTemplate['kompani1Sanitet'] = {
    'level' : 'komp',
    'units' : {
        'komp1SanitetTropp' : 1
    }
}

armyTemplate['komp1SanitetTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 10
    }
}


armyTemplate['HRS'] = {
    'level' : 'komp',
    'units' : {
        'HRSTropp' : 1
    }
}

armyTemplate['HRSTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 9
    }
}


armyTemplate['kompani1'] = {
    'level' : 'komp',
    'units' : {
        'evakueringstropp' : 3
    }
}

armyTemplate['evakueringstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}


armyTemplate['stridstrenbat'] = { #ca 500 soldater og befal
    'level' : 'bat',
    'units' : {
        'komp1Stridtren' : 1,   #Virker som at denne er ulik fra komp1 hos sanitet
        'komp2Stridtren' : 1,
        'komp3Stridtren' : 1,
        'komp4Stridtren' : 1
    }
}

armyTemplate['komp1Stridtren'] = {
    'level' : 'komp',
    'units' : {
        'komp1StridtrenTropp' : 1
    }
}

armyTemplate['komp1StridtrenTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 16
    }
}

armyTemplate['komp2Stridtren'] = {
    'level' : 'komp',
    'units' : {
        'komp2StridtrenTropp' : 1
    }
}

armyTemplate['komp2StridtrenTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 15
    }
}


armyTemplate['komp4Stridtren'] = {
    'level' : 'komp',
    'units' : {
        'vedlikeholdstropp' : 1,
        'tungtransportstropp' : 1,
        'transport' : 1,
        'servicetropp' : 1
    }
}

armyTemplate['vedlikeholdstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}

armyTemplate['tungtransportstropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}

armyTemplate['transport'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 3
    }
}

armyTemplate['servicetropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 4
    }
}

armyTemplate['finnmarklandforsvar'] = { #150 personer
    'level' : 'brig',
    'units' : {
        'finnmarkheimvern17' : 1,
        'porsangerbat' : 1
        # , 'grensevaktGarnisonen' : 1
    }
    }
armyTemplate['finnmarkheimvern17'] = {
    'level' : 'bat',
    'units' : {
        'finnmarkheimvern17komp' : 1
    }
}

armyTemplate['finnmarkheimvern17komp'] = {
    'level' : 'komp',
    'units' : {
        'finnmarkheimvern17trp' : 1
    }
}

armyTemplate['finnmarkheimvern17trp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 9
    }
}



armyTemplate['porsangerbat'] = {
    'level' : 'bat',
    'units' : {
        'porsangerkomp' : 1
    }
}

armyTemplate['porsangerkomp'] = {
    'level' : 'komp',
    'units' : {
        'porsangerTropp' : 1
    }
}

armyTemplate['porsangerTropp'] = {
    'level' : 'trp',
    'units' : {
        'lag' : 9
    }
}
