armyTemplate = {}

armyTemplate['brigardenord'] = {
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

armyTemplate['telemarkbat'] = {
    'stridsvogneskadron' : 1,  #Tar med i første omgang, selv om stridsvogner
    'kavalerieskadron' : 1, 
    'mekanisertinfant' : 2,
    'kampstøtteeskadron' : 1
}

armyTemplate['kampstøtteEskadron'] = {
    'eskadronstab' : 1,
    'sambandstropp' : 1,
    'repBergtropp' : 1,
    'bombekastropp' : 1,
    'sanitetstropp': 1
}

armyTemplate['eskadronstab'] = { #ikke tropp, men regner med samme antall lag
    'lag' : 4
}
armyTemplate['sambandstropp'] = {
    'lag' : 4
}

armyTemplate['repBergtropp'] = {
    'lag' : 4
}

armyTemplate['bombekastropp'] = {
    'lag' : 4
}
armyTemplate['sanitetstropp'] = {
    'lag' : 4
}
armyTemplate['lag'] = {
    'ansatte' : 8
}

armyTemplate['andrebat'] = {  #ca 600 menn på kompB, C, kavaleri, støttekomp, betaljonstab
    #'kompA' : 1,  i reserve, ikke i daglig drift
    'kompB' : 1, 
    'kompC' : 1,
    'kavalerieskadron' : 1,
    'støttekomp' : 1,
    'bataljonstab' : 1
    }

armyTemplate['kompB'] = {
    'lag' : 15
}

armyTemplate['kompC'] = {
    'lag' : 15
}

armyTemplate['støttekomp'] = {
    'lag' : 15
}

armyTemplate['bataljonstab'] = {
    'lag' : 15
}


armyTemplate['kavalerieskadron'] = { #15 lag igjen med 8 per
    'oppklaringstropp' : 1,
    'skarpskyttertropp' : 1,
    'MUAS' : 1
}
armyTemplate['oppklaringstropp'] = {
    'lag' = 5
}

armyTemplate['skarpskyttertropp'] = {
    'lag' = 5
}

armyTemplate['MUAS'] = {
    'lag' = 5
}

armyTemplate['panserbat'] = { #ca 560
    'kavalerieskadron' : 1, #18 lag
    'stridsvogneskadron' : 1, #17 lag
    'stormeskadron' : 2, #35 lag
    'kampstøtteeskadron' : 1 #18 lag
    }

armyTemplate['kavalerieskadron']= {  #18
    'oppklaringstropp' : 1,
    'patruljetropp' : 1,
    'sensortropp' : 1
}

armyTemplate['oppklaringstropp'] = {
    'lag' : 6
}
armyTemplate['patruljetropp'] = {
    'lag' : 6
}

armyTemplate['sensortropp'] = {
    'lag' : 6
}


armyTemplate['kampstøtteeskadron'] = { #18
    'kommandoplasstropp' : 1,
    'sanitetstropp' : 1,
    'stridstrentropp' : 1,
    'bombekastertropp' : 1
    }

armyTemplate['kommandoplasstropp'] = {
    'lag' : 4
}
armyTemplate['sanitetstropp'] = {
    'lag' : 5
}
armyTemplate['stridstrentropp'] = {
    'lag' : 4
}
armyTemplate['bombekastertropp'] = {
    'lag' : 4
}

# armyTemplate['strodstrentropp'] = {
#     'forsyningsgruppe' : 1,
#     'reperasjonsgruppe' : 1,
#     'bergningsgruppe' : 1
#     }


armyTemplate['artilleribat'] = { #ingen/lite info om antall eller tropper nedover
    'bataljonstab' : 1,
    'kanonbatteriNOP' : 1,
    'lokaliseringsbatteri' : 1,
    'stabsbatteri' : 1,
    'kampluftvernbatteri' : 1
}

armyTemplate['ingeniørbataljon'] = { #260 ansatte og 400 vernepliktige
    'Ingeniørkomp' : 6
}
armyTemplate['Ingeniørkomp'] = {
    'lag' = 5
}

armyTemplate['sambandsbat'] = { #ca 600
    'telekomp' : 1,
    'radiokomp' : 1,
    'kommandoplasskomp' : 1
}

armyTemplate['telekomp'] = {
    'lag' = 25
}
armyTemplate['radiokomp'] = {
    'lag' = 25
}
armyTemplate['kommandoplasskomp'] = {
    'lag' = 25
}

armyTemplate['sanitetsbat']={
    'sykehuskompani' : 1,
    'kompani1Sanitet' : 1,
    'HRS' : 1
}
armyTemplate['sykehuskompani'] = {
    'lag' = 9
}
armyTemplate['kompani1Sanitet'] = {
    'lag' = 10
}
armyTemplate['HRS'] = {
    'lag' = 9
}

armyTemplate['kompani1'] = {
    'evakueringstropp' : 3
}
armyTemplate['evakueringstropp'] {
    'lag' = 4
}

armyTemplate['stridstrenbat'] = { #ca 500 soldater og befal
    'komp1Stridtren' : 1,   #Virker som at denne er ulik fra komp1 hos sanitet
    'komp2Stridtren' : 1,
    'komp3Stridtren' : 1,
    'komp4Stridtren' : 1
}
armyTemplate['komp1Stridtren'] {
    'lag' = 16
}
armyTemplate['komp2Stridtren'] {
    'lag' = 15
}
armyTemplate['komp4Stridtren'] {
    'lag' = 16
}

armyTemplate['komp4Stridtren'] = {
    'vedlikeholdstropp' : 1,
    'tungtransportstropp' : 1,
    'transport' : 1,
    'servicetropp' : 1
}
armyTemplate['vedlikeholdstropp'] {
    'lag' = 4
}
armyTemplate['tungtransportstropp'] {
    'lag' = 4
}
armyTemplate['transport'] {
    'lag' = 3
}
armyTemplate['servicetropp'] = {
    'lag' = 4
}

armyTemplate['finnmarklandforsvar'] = { #150 personer
    'finnmarkheimvern17' : 1,
    'porsangerbat' : 1
    # , 'grensevaktGarnisonen' : 1
    }
armyTemplate['finnmarkheimvern17'] = {
    'lag' = 9
}
armyTemplate['porsangerbat'] = {
    'lag' = 9
}





