armyTemplate = {}

armyTemplate['brigardenord'] {
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


armyTemplate['andrebat'] = { 
    'kompA' : 1, # i reserve, ikke i daglig drift
    'kompB' : 1, 
    'kompC' : 1,
    'kavalerieskadron' : 1,
    'støttekomp' : 1,
    'bataljonstab' : 1
    }

armyTemplate['kavalerieskadron'] = {
    'oppklaringstropp' : 1,
    'skarpskyttertropp' : 1,
    'MUAS' : 1
}


armyTemplate['panserbat'] = {
    'kavalerieskadron' : 1,
    'stridsvogneskadron' : 1,
    'stormeskadron' : 2,
    'kampstøtteeskadron' : 1
    }

armyTemplate['kavalerieskadron']= {
    'oppklaringstropp' : 1,
    'patruljetropp' : 1,
    'sensortropp' : 1
}

armyTemplate['kampstøtteeskadron'] = {
    'kommandoplasstropp' : 1,
    'sanitetstropp' : 1,
    'stridstrentropp' : 1,
    'bombekastertropp' : 1
    }

armyTemplate['strodstrentropp'] = {
    'forsyningsgruppe' : 1,
    'reperasjonsgruppe' : 1,
    'bergningsgruppe' : 1
    }


armyTemplate['artilleribat'] = {
    'bataljonstab' : 1,
    'kanonbatteriNOP' : 1,
    'lokaliseringsbatteri' : 1,
    'stabsbatteri' : 1,
    'kampluftvernbatteri' : 1
}


armyTemplate['ingeniørbataljon'] = { #260 ansatte og 400 vernepliktige
    'Ingeniørkomp' : 6
}

armyTemplate['sambandsbat'] = {
    'telekomp' : 1,
    'radiokomp' : 1,
    'kommandoplasskomp' : 1
}


armyTemplate['sanitetsbat']={
    'sykehuskompani' : 1,
    'kompani1Sanitet' : 1,
    'HRS' : 1
}

armyTemplate['kompani1'] = {
    'evakueringstropp' : 3
}

armyTemplate['stridstrenbat'] = { #ca 500 soldater og befal
    'komp1Stridtren' : 1,   #Virker som at denne er ulik fra komp1 hos sanitet
    'komp2Stridtren' : 1,
    'komp3Stridtren' : 1,
    'komp4Stridtren' : 1
}

armyTemplate['komp4Stridtren'] = {
    'vedlikeholdstropp' : 1,
    'tungtransportstropp' : 1,
    'transport' : 1,
    'servicetropp' : 1
}

armyTemplate['finnmarklandforsvar'] = {
    'finnmarkheimvern17' : 1,
    'porsangerbat' : 1
    # , 'grensevaktGarnisonen' : 1
    }




