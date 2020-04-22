#py -3 -m venv .venv
#Set-ExecutionPolicy Unrestricted -Force
#.venv\scripts\activate
#py -3 -m pip install --upgrade pip
#py -3 -m pip install matplotlib
#py -3 -m pip install pyjstat
#py -3 -m pip install requests

#.\.venv\Scripts\python.exe -m pip install --upgrade pip
#.\.venv\Scripts\python.exe -m pip install matplotlib
#.\.venv\Scripts\python.exe -m pip install pyjstat
#.\.venv\Scripts\python.exe -m pip install requests

	#07459: Population, by sex and one-year age groups (M) 1986 - 2020
#09747: Private households, persons in private households and persons per private houshold (M) (UD) 2005 - 2019
#05530: Mean age of parents at all birth
#10995: Families, by type of family and the number of children 0-17 years living at home (C) 2005 - 2019
	#06206: Children 0-17 years, by number of siblings and the child's age 2001 - 2019
	#06079: Private households and persons in private households, by size of household (per cent) (M) (UD) 2005 - 2019
#06091: Persons in couples with and without children in private households, by cohabiting arrangements and age 2005 - 2019

#05232: Pupils in primary and lower secondary school, by class level, tenure status and type of institution (C) 2002 - 2019
#08947: Pupils, apprentices, students and participants in upper secondary education, by sex, age and type of school/institution 2006 - 2019
#12932: Teaching positions for upper secondary education, by sex, age groups and full-time and part-time positions (C) 2015 - 2019
#12712: Employees working with the children/pupils in upper secondary school, by sex, age and immigration category 2015 - 2018

#06070: Privathusholdninger, etter husholdningstype (K) (B) 2005 - 2019
#06844: Personer 67 år og over i privathusholdninger, etter alder og antall personer i husholdningen (K) (B) 1960 - 2019
#04469: Bebuarar i bustader kommunen disponerer til pleie- og omsorgsformål, etter alder (K) 2002 - 2018


####################

#STRAT:
	#07459: Population, by sex and one-year age groups (M) 1986 - 2020
	#06079: Private households and persons in private households, by size of household (per cent) (M) (UD) 2005 - 2019
	#06070: Privathusholdninger, etter husholdningstype (K) (B) 2005 - 2019
	#06206: Children 0-17 years, by number of siblings and the child's age 2001 - 2019
	#08947: Pupils, apprentices, students and participants in upper secondary education, by sex, age and type of school/institution 2006 - 2019
	#06844: Personer 67 år og over i privathusholdninger, etter alder og antall personer i husholdningen (K) (B) 1960 - 2019
  #10308: Establishments, by the enterprises sector and number of employees (M) 2012 - 2020
	#Skoler: antall og størrelse

	#Mao hvis familie F1 er på barneskole BA og ungdomsskole UA, og familie F2 også er på barneskole BA, er det ikke noe mer sannsynlig at de er på ungdomsskole UA enn på en annen ungdomsskole

####################

# Post query and get Pandas dataframe in return
# use library pyjstat for JSON-stat
from pyjstat import pyjstat
import requests
import subprocess
import json
import pandas as pd
import os

def generateDemographicData():

  dirname = os.path.dirname(__file__)
  dirname = dirname+"/populationData/"
  try:
    os.mkdir(dirname)
  except:
    print("Directory 'populationData' already exists")

  #retrieving school data:

  headers = {
      'Accept': 'application/json',
  }

  #This bit of code fetches the list of all schools in the country and filters out the inactive ones and the ones that... aren't schools
  print("Fetching list of all schools")
  result = requests.get('https://data-nsr.udir.no/enheter', headers=headers)
  print(result) 
  schools_dataFrame = pd.read_json(result.text)
  schools_dataFrame.to_csv(dirname+'schools.csv')
  # schools_dataFrame = pd.read_csv(dirname+"schools.csv")
  activeSchools = schools_dataFrame.loc[schools_dataFrame['ErAktiv'] == True]
  activeSchools = activeSchools.loc[activeSchools['ErSkole'] == True]

  #This bit of code fetches the more complete information for all the codes, including, crucially numbers of pupils and employees
  print("Fetching detailed data on all active schools")
  nsrIdList = activeSchools['NSRId'].to_list()
  url = 'https://data-nsr.udir.no/enhet/'+str(nsrIdList[0])
  result = requests.get(url, headers=headers)
  allSchoolData = pd.read_json("["+result.text+"]")
  # for i in range(1,10):
  for i in range(1,activeSchools.shape[0]):
    url = 'https://data-nsr.udir.no/enhet/'+str(nsrIdList[i])
    result = requests.get(url, headers=headers)
    print(url+" "+str(result)+"  "+str(i)+"/"+str(activeSchools.shape[0]))
    schoolData = pd.read_json("["+result.text+"]")
    allSchoolData = pd.concat([allSchoolData,schoolData])
  print(allSchoolData)
  allSchoolData.to_csv(dirname+'allSchools.csv')

  #################################################

  # 07459: Population, by region, age, contents and year
  print("Fetching SSB dataset: 07459: Population, by region, age, contents and year")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/07459'

  # API query  - All people in all places of all ages by age, 2020
  payload = {
    "query": [
      {
        "code": "Region",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Kjonn",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Alder",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "item",
          "values": [
            "Personer1"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2020"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  pop_age_region_dataFrame = dataset.write('dataframe')
  # pop_age_region_dataFrame.head()
  # pop_age_region_dataFrame.tail()
  # pop_age_region_dataFrame.info()

  #pop_age_region_dataFrame.to_dict
  #list(pop_age_region_dataFrame.columns.values)
  #print(pop_age_region_dataFrame)

  pop_age_region_dataFrame.to_csv(dirname+'pop_age_region.csv')

  #################################################

  # 06079: Private households and persons in private households, by size of household (per cent) (M) (UD) 2005 - 2019
  print("Fetching SSB dataset: 06079: Private households and persons in private households, by size of household (per cent) (M) (UD) 2005 - 2019")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/06079'

  # API query  - Size of households by region
  payload = {
    "query": [
      {
        "code": "Region",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "HushStr",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2019"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  household_sizes_dataFrame = dataset.write('dataframe')
  household_sizes_dataFrame.to_csv(dirname+'household_sizes.csv')


  #################################################

  #06070: Privathusholdninger, etter husholdningstype (K) (B) 2005 - 2019
  print("Fetching SSB dataset: 06070: Privathusholdninger, etter husholdningstype (K) (B) 2005 - 2019")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/06070'

  # API query  - Household types by region (single parent or not, etc.)
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "agg:KommSummer",
        "values": [
          "K-3001",
          "K-3002",
          "K-3003",
          "K-3004",
          "K-3005",
          "K-3006",
          "K-3007",
          "K-3011",
          "K-3012",
          "K-3013",
          "K-3014",
          "K-3015",
          "K-3016",
          "K-3017",
          "K-3018",
          "K-3019",
          "K-3020",
          "K-3021",
          "K-3022",
          "K-3023",
          "K-3024",
          "K-3025",
          "K-3026",
          "K-3027",
          "K-3028",
          "K-3029",
          "K-3030",
          "K-3031",
          "K-3032",
          "K-3033",
          "K-3034",
          "K-3035",
          "K-3036",
          "K-3037",
          "K-3038",
          "K-3039",
          "K-3040",
          "K-3041",
          "K-3042",
          "K-3043",
          "K-3044",
          "K-3045",
          "K-3046",
          "K-3047",
          "K-3048",
          "K-3049",
          "K-3050",
          "K-3051",
          "K-3052",
          "K-3053",
          "K-3054",
          "K-0301",
          "K-3401",
          "K-3403",
          "K-3405",
          "K-3407",
          "K-3411",
          "K-3412",
          "K-3413",
          "K-3414",
          "K-3415",
          "K-3416",
          "K-3417",
          "K-3418",
          "K-3419",
          "K-3420",
          "K-3421",
          "K-3422",
          "K-3423",
          "K-3424",
          "K-3425",
          "K-3426",
          "K-3427",
          "K-3428",
          "K-3429",
          "K-3430",
          "K-3431",
          "K-3432",
          "K-3433",
          "K-3434",
          "K-3435",
          "K-3436",
          "K-3437",
          "K-3438",
          "K-3439",
          "K-3440",
          "K-3441",
          "K-3442",
          "K-3443",
          "K-3446",
          "K-3447",
          "K-3448",
          "K-3449",
          "K-3450",
          "K-3451",
          "K-3452",
          "K-3453",
          "K-3454",
          "K-3801",
          "K-3802",
          "K-3803",
          "K-3804",
          "K-3805",
          "K-3806",
          "K-3807",
          "K-3808",
          "K-3811",
          "K-3812",
          "K-3813",
          "K-3814",
          "K-3815",
          "K-3816",
          "K-3817",
          "K-3818",
          "K-3819",
          "K-3820",
          "K-3821",
          "K-3822",
          "K-3823",
          "K-3824",
          "K-3825",
          "K-4201",
          "K-4202",
          "K-4203",
          "K-4204",
          "K-4205",
          "K-4206",
          "K-4207",
          "K-4211",
          "K-4212",
          "K-4213",
          "K-4214",
          "K-4215",
          "K-4216",
          "K-4217",
          "K-4218",
          "K-4219",
          "K-4220",
          "K-4221",
          "K-4222",
          "K-4223",
          "K-4224",
          "K-4225",
          "K-4226",
          "K-4227",
          "K-4228",
          "K-1101",
          "K-1103",
          "K-1106",
          "K-1108",
          "K-1111",
          "K-1112",
          "K-1114",
          "K-1119",
          "K-1120",
          "K-1121",
          "K-1122",
          "K-1124",
          "K-1127",
          "K-1130",
          "K-1133",
          "K-1134",
          "K-1135",
          "K-1144",
          "K-1145",
          "K-1146",
          "K-1149",
          "K-1151",
          "K-1160",
          "K-4601",
          "K-4602",
          "K-4611",
          "K-4612",
          "K-4613",
          "K-4614",
          "K-4615",
          "K-4616",
          "K-4617",
          "K-4618",
          "K-4619",
          "K-4620",
          "K-4621",
          "K-4622",
          "K-4623",
          "K-4624",
          "K-4625",
          "K-4626",
          "K-4627",
          "K-4628",
          "K-4629",
          "K-4630",
          "K-4631",
          "K-4632",
          "K-4633",
          "K-4634",
          "K-4635",
          "K-4636",
          "K-4637",
          "K-4638",
          "K-4639",
          "K-4640",
          "K-4641",
          "K-4642",
          "K-4643",
          "K-4644",
          "K-4645",
          "K-4646",
          "K-4647",
          "K-4648",
          "K-4649",
          "K-4650",
          "K-4651",
          "K-1505",
          "K-1506",
          "K-1507",
          "K-1511",
          "K-1514",
          "K-1515",
          "K-1516",
          "K-1517",
          "K-1520",
          "K-1525",
          "K-1528",
          "K-1531",
          "K-1532",
          "K-1535",
          "K-1539",
          "K-1547",
          "K-1554",
          "K-1557",
          "K-1560",
          "K-1563",
          "K-1566",
          "K-1573",
          "K-1576",
          "K-1577",
          "K-1578",
          "K-1579",
          "K-5001",
          "K-5006",
          "K-5007",
          "K-5014",
          "K-5020",
          "K-5021",
          "K-5022",
          "K-5025",
          "K-5026",
          "K-5027",
          "K-5028",
          "K-5029",
          "K-5031",
          "K-5032",
          "K-5033",
          "K-5034",
          "K-5035",
          "K-5036",
          "K-5037",
          "K-5038",
          "K-5041",
          "K-5042",
          "K-5043",
          "K-5044",
          "K-5045",
          "K-5046",
          "K-5047",
          "K-5049",
          "K-5052",
          "K-5053",
          "K-5054",
          "K-5055",
          "K-5056",
          "K-5057",
          "K-5058",
          "K-5059",
          "K-5060",
          "K-5061",
          "K-1804",
          "K-1806",
          "K-1811",
          "K-1812",
          "K-1813",
          "K-1815",
          "K-1816",
          "K-1818",
          "K-1820",
          "K-1822",
          "K-1824",
          "K-1825",
          "K-1826",
          "K-1827",
          "K-1828",
          "K-1832",
          "K-1833",
          "K-1834",
          "K-1835",
          "K-1836",
          "K-1837",
          "K-1838",
          "K-1839",
          "K-1840",
          "K-1841",
          "K-1845",
          "K-1848",
          "K-1851",
          "K-1853",
          "K-1856",
          "K-1857",
          "K-1859",
          "K-1860",
          "K-1865",
          "K-1866",
          "K-1867",
          "K-1868",
          "K-1870",
          "K-1871",
          "K-1874",
          "K-1875",
          "K-5401",
          "K-5402",
          "K-5403",
          "K-5404",
          "K-5405",
          "K-5406",
          "K-5411",
          "K-5412",
          "K-5413",
          "K-5414",
          "K-5415",
          "K-5416",
          "K-5417",
          "K-5418",
          "K-5419",
          "K-5420",
          "K-5421",
          "K-5422",
          "K-5423",
          "K-5424",
          "K-5425",
          "K-5426",
          "K-5427",
          "K-5428",
          "K-5429",
          "K-5430",
          "K-5432",
          "K-5433",
          "K-5434",
          "K-5435",
          "K-5436",
          "K-5437",
          "K-5438",
          "K-5439",
          "K-5440",
          "K-5441",
          "K-5442",
          "K-5443",
          "K-5444",
          "K-21-22",
          "K-23",
          "K-Rest"
        ]
      }
    },
    {
      "code": "HushType",
      "selection": {
        "filter": "item",
        "values": [
          "001",
          "002",
          "003",
          "004",
          "005",
          "006",
          "007",
          "008",
          "009",
          "010",
          "000"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}


  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  household_type_dataFrame = dataset.write('dataframe')
  household_type_dataFrame.to_csv(dirname+'household_type.csv')

  #################################################

  # 06206: Children 0-17 years, by number of siblings and the child's age 2001 - 2019
  print("Fetching SSB dataset: 06206: Children 0-17 years, by number of siblings and the child's age 2001 - 2019")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/06206'

  # API query  - Children 0-17, by number of siblings and age 2019
  payload = {
    "query": [
      {
        "code": "Alder",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2019"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  child_sibs_age_dataFrame = dataset.write('dataframe')
  child_sibs_age_dataFrame.to_csv(dirname+'child_sibs_age.csv')

  #################################################

  #08947: Pupils, apprentices, students and participants in upper secondary education, by sex, age and type of school/institution 2006 - 2019
  print("Fetching SSB dataset: 08947: Pupils, apprentices, students and participants in upper secondary education, by sex, age and type of school/institution 2006 - 2019")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/08947'

  # API query - Upper secondary schoolers
  payload = {
    "query": [
      {
        "code": "Skoleslag",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Kjonn",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Alder",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "item",
          "values": [
            "EleverVidereg"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2019"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }


  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  upper_secondary_schoolers_dataFrame = dataset.write('dataframe')
  upper_secondary_schoolers_dataFrame.to_csv(dirname+'upper_secondary_schoolers.csv')

  #################################################

  #06844: Personer 67 år og over i privathusholdninger, etter alder og antall personer i husholdningen (K) (B) 1960 - 2019
  print("Fetching SSB dataset: 06844: Personer 67 år og over i privathusholdninger, etter alder og antall personer i husholdningen (K) (B) 1960 - 2019")
  POST_URL = 'https://data.ssb.no/api/v0/en/table/06844'

  # API query - Old people in households
  payload = {
    "query": [
      {
        "code": "Region",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Alder",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2019"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }


  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  old_in_household_dataFrame = dataset.write('dataframe')
  old_in_household_dataFrame.to_csv(dirname+'old_in_household.csv')

  #################################################

  #10308: Establishments, by the enterprises sector and number of employees (M) 2012 - 2020
  print("Fetching SSB dataset: 10308: Establishments, by the enterprises sector and number of employees (M) 2012 - 2020")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/10308'

  # API query  - 
  payload = {
    "query": [
      {
        "code": "Region",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "Eiersektor",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "AntAnsatte",
        "selection": {
          "filter": "all",
          "values": [
            "*"
          ]
        }
      },
      {
        "code": "ContentsCode",
        "selection": {
          "filter": "item",
          "values": [
            "Virksheter"
          ]
        }
      },
      {
        "code": "Tid",
        "selection": {
          "filter": "item",
          "values": [
            "2020"
          ]
        }
      }
    ],
    "response": {
      "format": "json-stat2"
    }
  }

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  establishments_dataFrame = dataset.write('dataframe')
  establishments_dataFrame.to_csv(dirname+'establishments.csv')

  #################################################

  #04469: Bebuarar i bustader kommunen disponerer til pleie- og omsorgsformål, etter alder (K) 2002 - 2018
  print("Fetching SSB dataset: 04469: Bebuarar i bustader kommunen disponerer til pleie- og omsorgsformål, etter alder (K) 2002 - 2018")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/04469'

  # API query  - people in elderly homes osv.
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "Alder",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "ContentsCode",
      "selection": {
        "filter": "item",
        "values": [
          "Beboere",
          "BeboerePrInnbygg"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2018"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}


  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  nursing_patients_dataFrame = dataset.write('dataframe')
  nursing_patients_dataFrame.to_csv(dirname+'nursing_patients.csv')

#################################################

#09929: Nursing and care institutions and beds, by ownership (C) 2009 - 2018
  print("Fetching SSB dataset: 09929: Nursing and care institutions and beds, by ownership (C) 2009 - 2018")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/09929'

  # API query  - beds in old people homes
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "vs:FylkerFastland",
        "values": [
          "30",
          "01",
          "02",
          "06",
          "03",
          "34",
          "04",
          "05",
          "38",
          "07",
          "08",
          "42",
          "09",
          "10",
          "11",
          "46",
          "12",
          "14",
          "15",
          "50",
          "16",
          "17",
          "18",
          "54",
          "19",
          "20",
          "21"
        ]
      }
    },
    {
      "code": "Eigarforhold",
      "selection": {
        "filter": "item",
        "values": [
          "0"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2018"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  nursing_spots_dataFrame = dataset.write('dataframe')
  nursing_spots_dataFrame.to_csv(dirname+'nursing_spots.csv')

  #################################################

  #09220: Kindergartens, by ownership (M) 1987 - 2019
  print("Fetching SSB dataset: 09220: Kindergartens, by ownership (M) 1987 - 2019")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/09220'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "agg:KommSummer",
        "values": [
          "K-3001",
          "K-3002",
          "K-3003",
          "K-3004",
          "K-3005",
          "K-3006",
          "K-3007",
          "K-3011",
          "K-3012",
          "K-3013",
          "K-3014",
          "K-3015",
          "K-3016",
          "K-3017",
          "K-3018",
          "K-3019",
          "K-3020",
          "K-3021",
          "K-3022",
          "K-3023",
          "K-3024",
          "K-3025",
          "K-3026",
          "K-3027",
          "K-3028",
          "K-3029",
          "K-3030",
          "K-3031",
          "K-3032",
          "K-3033",
          "K-3034",
          "K-3035",
          "K-3036",
          "K-3037",
          "K-3038",
          "K-3039",
          "K-3040",
          "K-3041",
          "K-3042",
          "K-3043",
          "K-3044",
          "K-3045",
          "K-3046",
          "K-3047",
          "K-3048",
          "K-3049",
          "K-3050",
          "K-3051",
          "K-3052",
          "K-3053",
          "K-3054",
          "K-0301",
          "K-3401",
          "K-3403",
          "K-3405",
          "K-3407",
          "K-3411",
          "K-3412",
          "K-3413",
          "K-3414",
          "K-3415",
          "K-3416",
          "K-3417",
          "K-3418",
          "K-3419",
          "K-3420",
          "K-3421",
          "K-3422",
          "K-3423",
          "K-3424",
          "K-3425",
          "K-3426",
          "K-3427",
          "K-3428",
          "K-3429",
          "K-3430",
          "K-3431",
          "K-3432",
          "K-3433",
          "K-3434",
          "K-3435",
          "K-3436",
          "K-3437",
          "K-3438",
          "K-3439",
          "K-3440",
          "K-3441",
          "K-3442",
          "K-3443",
          "K-3446",
          "K-3447",
          "K-3448",
          "K-3449",
          "K-3450",
          "K-3451",
          "K-3452",
          "K-3453",
          "K-3454",
          "K-3801",
          "K-3802",
          "K-3803",
          "K-3804",
          "K-3805",
          "K-3806",
          "K-3807",
          "K-3808",
          "K-3811",
          "K-3812",
          "K-3813",
          "K-3814",
          "K-3815",
          "K-3816",
          "K-3817",
          "K-3818",
          "K-3819",
          "K-3820",
          "K-3821",
          "K-3822",
          "K-3823",
          "K-3824",
          "K-3825",
          "K-4201",
          "K-4202",
          "K-4203",
          "K-4204",
          "K-4205",
          "K-4206",
          "K-4207",
          "K-4211",
          "K-4212",
          "K-4213",
          "K-4214",
          "K-4215",
          "K-4216",
          "K-4217",
          "K-4218",
          "K-4219",
          "K-4220",
          "K-4221",
          "K-4222",
          "K-4223",
          "K-4224",
          "K-4225",
          "K-4226",
          "K-4227",
          "K-4228",
          "K-1101",
          "K-1103",
          "K-1106",
          "K-1108",
          "K-1111",
          "K-1112",
          "K-1114",
          "K-1119",
          "K-1120",
          "K-1121",
          "K-1122",
          "K-1124",
          "K-1127",
          "K-1130",
          "K-1133",
          "K-1134",
          "K-1135",
          "K-1144",
          "K-1145",
          "K-1146",
          "K-1149",
          "K-1151",
          "K-1160",
          "K-4601",
          "K-4602",
          "K-4611",
          "K-4612",
          "K-4613",
          "K-4614",
          "K-4615",
          "K-4616",
          "K-4617",
          "K-4618",
          "K-4619",
          "K-4620",
          "K-4621",
          "K-4622",
          "K-4623",
          "K-4624",
          "K-4625",
          "K-4626",
          "K-4627",
          "K-4628",
          "K-4629",
          "K-4630",
          "K-4631",
          "K-4632",
          "K-4633",
          "K-4634",
          "K-4635",
          "K-4636",
          "K-4637",
          "K-4638",
          "K-4639",
          "K-4640",
          "K-4641",
          "K-4642",
          "K-4643",
          "K-4644",
          "K-4645",
          "K-4646",
          "K-4647",
          "K-4648",
          "K-4649",
          "K-4650",
          "K-4651",
          "K-1505",
          "K-1506",
          "K-1507",
          "K-1511",
          "K-1514",
          "K-1515",
          "K-1516",
          "K-1517",
          "K-1520",
          "K-1525",
          "K-1528",
          "K-1531",
          "K-1532",
          "K-1535",
          "K-1539",
          "K-1547",
          "K-1554",
          "K-1557",
          "K-1560",
          "K-1563",
          "K-1566",
          "K-1573",
          "K-1576",
          "K-1577",
          "K-1578",
          "K-1579",
          "K-5001",
          "K-5006",
          "K-5007",
          "K-5014",
          "K-5020",
          "K-5021",
          "K-5022",
          "K-5025",
          "K-5026",
          "K-5027",
          "K-5028",
          "K-5029",
          "K-5031",
          "K-5032",
          "K-5033",
          "K-5034",
          "K-5035",
          "K-5036",
          "K-5037",
          "K-5038",
          "K-5041",
          "K-5042",
          "K-5043",
          "K-5044",
          "K-5045",
          "K-5046",
          "K-5047",
          "K-5049",
          "K-5052",
          "K-5053",
          "K-5054",
          "K-5055",
          "K-5056",
          "K-5057",
          "K-5058",
          "K-5059",
          "K-5060",
          "K-5061",
          "K-1804",
          "K-1806",
          "K-1811",
          "K-1812",
          "K-1813",
          "K-1815",
          "K-1816",
          "K-1818",
          "K-1820",
          "K-1822",
          "K-1824",
          "K-1825",
          "K-1826",
          "K-1827",
          "K-1828",
          "K-1832",
          "K-1833",
          "K-1834",
          "K-1835",
          "K-1836",
          "K-1837",
          "K-1838",
          "K-1839",
          "K-1840",
          "K-1841",
          "K-1845",
          "K-1848",
          "K-1851",
          "K-1853",
          "K-1856",
          "K-1857",
          "K-1859",
          "K-1860",
          "K-1865",
          "K-1866",
          "K-1867",
          "K-1868",
          "K-1870",
          "K-1871",
          "K-1874",
          "K-1875",
          "K-5401",
          "K-5402",
          "K-5403",
          "K-5404",
          "K-5405",
          "K-5406",
          "K-5411",
          "K-5412",
          "K-5413",
          "K-5414",
          "K-5415",
          "K-5416",
          "K-5417",
          "K-5418",
          "K-5419",
          "K-5420",
          "K-5421",
          "K-5422",
          "K-5423",
          "K-5424",
          "K-5425",
          "K-5426",
          "K-5427",
          "K-5428",
          "K-5429",
          "K-5430",
          "K-5432",
          "K-5433",
          "K-5434",
          "K-5435",
          "K-5436",
          "K-5437",
          "K-5438",
          "K-5439",
          "K-5440",
          "K-5441",
          "K-5442",
          "K-5443",
          "K-5444",
          "K-21-22",
          "K-23",
          "K-Rest"
        ]
      }
    },
    {
      "code": "Eierskap",
      "selection": {
        "filter": "item",
        "values": [
          "01",
          "02-03",
          "98"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  kindergartenNumbers_dataFrame = dataset.write('dataframe')
  kindergartenNumbers_dataFrame.to_csv(dirname+'kindergartenNumbers.csv')

  #################################################

  #09169: Barn i barnehager, etter region, barnehagetype, statistikkvariabel og år
  print("Fetching SSB dataset: 09169: Barn i barnehager, etter region, barnehagetype, statistikkvariabel og år")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/09169'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "agg:KommSummer",
        "values": [
          "K-3001",
          "K-3002",
          "K-3003",
          "K-3004",
          "K-3005",
          "K-3006",
          "K-3007",
          "K-3011",
          "K-3012",
          "K-3013",
          "K-3014",
          "K-3015",
          "K-3016",
          "K-3017",
          "K-3018",
          "K-3019",
          "K-3020",
          "K-3021",
          "K-3022",
          "K-3023",
          "K-3024",
          "K-3025",
          "K-3026",
          "K-3027",
          "K-3028",
          "K-3029",
          "K-3030",
          "K-3031",
          "K-3032",
          "K-3033",
          "K-3034",
          "K-3035",
          "K-3036",
          "K-3037",
          "K-3038",
          "K-3039",
          "K-3040",
          "K-3041",
          "K-3042",
          "K-3043",
          "K-3044",
          "K-3045",
          "K-3046",
          "K-3047",
          "K-3048",
          "K-3049",
          "K-3050",
          "K-3051",
          "K-3052",
          "K-3053",
          "K-3054",
          "K-0301",
          "K-3401",
          "K-3403",
          "K-3405",
          "K-3407",
          "K-3411",
          "K-3412",
          "K-3413",
          "K-3414",
          "K-3415",
          "K-3416",
          "K-3417",
          "K-3418",
          "K-3419",
          "K-3420",
          "K-3421",
          "K-3422",
          "K-3423",
          "K-3424",
          "K-3425",
          "K-3426",
          "K-3427",
          "K-3428",
          "K-3429",
          "K-3430",
          "K-3431",
          "K-3432",
          "K-3433",
          "K-3434",
          "K-3435",
          "K-3436",
          "K-3437",
          "K-3438",
          "K-3439",
          "K-3440",
          "K-3441",
          "K-3442",
          "K-3443",
          "K-3446",
          "K-3447",
          "K-3448",
          "K-3449",
          "K-3450",
          "K-3451",
          "K-3452",
          "K-3453",
          "K-3454",
          "K-3801",
          "K-3802",
          "K-3803",
          "K-3804",
          "K-3805",
          "K-3806",
          "K-3807",
          "K-3808",
          "K-3811",
          "K-3812",
          "K-3813",
          "K-3814",
          "K-3815",
          "K-3816",
          "K-3817",
          "K-3818",
          "K-3819",
          "K-3820",
          "K-3821",
          "K-3822",
          "K-3823",
          "K-3824",
          "K-3825",
          "K-4201",
          "K-4202",
          "K-4203",
          "K-4204",
          "K-4205",
          "K-4206",
          "K-4207",
          "K-4211",
          "K-4212",
          "K-4213",
          "K-4214",
          "K-4215",
          "K-4216",
          "K-4217",
          "K-4218",
          "K-4219",
          "K-4220",
          "K-4221",
          "K-4222",
          "K-4223",
          "K-4224",
          "K-4225",
          "K-4226",
          "K-4227",
          "K-4228",
          "K-1101",
          "K-1103",
          "K-1106",
          "K-1108",
          "K-1111",
          "K-1112",
          "K-1114",
          "K-1119",
          "K-1120",
          "K-1121",
          "K-1122",
          "K-1124",
          "K-1127",
          "K-1130",
          "K-1133",
          "K-1134",
          "K-1135",
          "K-1144",
          "K-1145",
          "K-1146",
          "K-1149",
          "K-1151",
          "K-1160",
          "K-4601",
          "K-4602",
          "K-4611",
          "K-4612",
          "K-4613",
          "K-4614",
          "K-4615",
          "K-4616",
          "K-4617",
          "K-4618",
          "K-4619",
          "K-4620",
          "K-4621",
          "K-4622",
          "K-4623",
          "K-4624",
          "K-4625",
          "K-4626",
          "K-4627",
          "K-4628",
          "K-4629",
          "K-4630",
          "K-4631",
          "K-4632",
          "K-4633",
          "K-4634",
          "K-4635",
          "K-4636",
          "K-4637",
          "K-4638",
          "K-4639",
          "K-4640",
          "K-4641",
          "K-4642",
          "K-4643",
          "K-4644",
          "K-4645",
          "K-4646",
          "K-4647",
          "K-4648",
          "K-4649",
          "K-4650",
          "K-4651",
          "K-1505",
          "K-1506",
          "K-1507",
          "K-1511",
          "K-1514",
          "K-1515",
          "K-1516",
          "K-1517",
          "K-1520",
          "K-1525",
          "K-1528",
          "K-1531",
          "K-1532",
          "K-1535",
          "K-1539",
          "K-1547",
          "K-1554",
          "K-1557",
          "K-1560",
          "K-1563",
          "K-1566",
          "K-1573",
          "K-1576",
          "K-1577",
          "K-1578",
          "K-1579",
          "K-5001",
          "K-5006",
          "K-5007",
          "K-5014",
          "K-5020",
          "K-5021",
          "K-5022",
          "K-5025",
          "K-5026",
          "K-5027",
          "K-5028",
          "K-5029",
          "K-5031",
          "K-5032",
          "K-5033",
          "K-5034",
          "K-5035",
          "K-5036",
          "K-5037",
          "K-5038",
          "K-5041",
          "K-5042",
          "K-5043",
          "K-5044",
          "K-5045",
          "K-5046",
          "K-5047",
          "K-5049",
          "K-5052",
          "K-5053",
          "K-5054",
          "K-5055",
          "K-5056",
          "K-5057",
          "K-5058",
          "K-5059",
          "K-5060",
          "K-5061",
          "K-1804",
          "K-1806",
          "K-1811",
          "K-1812",
          "K-1813",
          "K-1815",
          "K-1816",
          "K-1818",
          "K-1820",
          "K-1822",
          "K-1824",
          "K-1825",
          "K-1826",
          "K-1827",
          "K-1828",
          "K-1832",
          "K-1833",
          "K-1834",
          "K-1835",
          "K-1836",
          "K-1837",
          "K-1838",
          "K-1839",
          "K-1840",
          "K-1841",
          "K-1845",
          "K-1848",
          "K-1851",
          "K-1853",
          "K-1856",
          "K-1857",
          "K-1859",
          "K-1860",
          "K-1865",
          "K-1866",
          "K-1867",
          "K-1868",
          "K-1870",
          "K-1871",
          "K-1874",
          "K-1875",
          "K-5401",
          "K-5402",
          "K-5403",
          "K-5404",
          "K-5405",
          "K-5406",
          "K-5411",
          "K-5412",
          "K-5413",
          "K-5414",
          "K-5415",
          "K-5416",
          "K-5417",
          "K-5418",
          "K-5419",
          "K-5420",
          "K-5421",
          "K-5422",
          "K-5423",
          "K-5424",
          "K-5425",
          "K-5426",
          "K-5427",
          "K-5428",
          "K-5429",
          "K-5430",
          "K-5432",
          "K-5433",
          "K-5434",
          "K-5435",
          "K-5436",
          "K-5437",
          "K-5438",
          "K-5439",
          "K-5440",
          "K-5441",
          "K-5442",
          "K-5443",
          "K-5444",
          "K-21-22",
          "K-23",
          "K-Rest"
        ]
      }
    },
    {
      "code": "Alder",
      "selection": {
        "filter": "item",
        "values": [
          "000",
          "001",
          "002",
          "003",
          "004",
          "005",
          "006",
          "888"
        ]
      }
    },
    {
      "code": "BarnehageType",
      "selection": {
        "filter": "item",
        "values": [
          "01",
          "02-03",
          "98"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  kidsInKindergartens_dataFrame = dataset.write('dataframe')
  kidsInKindergartens_dataFrame.to_csv(dirname+'kidsInKindergartens.csv')

  #################################################

  #11933: Care institutions - rooms, by region, contents and year
  print("Fetching SSB dataset: 11933: Care institutions - rooms, by region, contents and year")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/11933'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  nursingHomeRooms_dataFrame = dataset.write('dataframe')
  nursingHomeRooms_dataFrame.to_csv(dirname+'nursingHomeRooms.csv')


  #################################################
  #12562: Selected key figures kindergartens, by region, contents and year
  print("Fetching SSB dataset: 12562: Selected key figures kindergartens, by region, contents and year")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/12562'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "KOKkommuneregion0000",
      "selection": {
        "filter": "agg_single:KOGkommuneregion000000904",
        "values": [
          "0101",
          "0104",
          "0105",
          "0106",
          "0111",
          "0118",
          "0119",
          "0121",
          "0122",
          "0123",
          "0124",
          "0125",
          "0127",
          "0128",
          "0135",
          "0136",
          "0137",
          "0138",
          "0211",
          "0213",
          "0214",
          "0215",
          "0216",
          "0217",
          "0219",
          "0220",
          "0221",
          "0226",
          "0227",
          "0228",
          "0229",
          "0230",
          "0231",
          "0233",
          "0234",
          "0235",
          "0236",
          "0237",
          "0238",
          "0239",
          "0301",
          "0402",
          "0403",
          "0412",
          "0415",
          "0417",
          "0418",
          "0419",
          "0420",
          "0423",
          "0425",
          "0426",
          "0427",
          "0428",
          "0429",
          "0430",
          "0432",
          "0434",
          "0436",
          "0437",
          "0438",
          "0439",
          "0441",
          "0501",
          "0502",
          "0511",
          "0512",
          "0513",
          "0514",
          "0515",
          "0516",
          "0517",
          "0519",
          "0520",
          "0521",
          "0522",
          "0528",
          "0529",
          "0532",
          "0533",
          "0534",
          "0536",
          "0538",
          "0540",
          "0541",
          "0542",
          "0543",
          "0544",
          "0545",
          "0602",
          "0604",
          "0605",
          "0612",
          "0615",
          "0616",
          "0617",
          "0618",
          "0619",
          "0620",
          "0621",
          "0622",
          "0623",
          "0624",
          "0625",
          "0626",
          "0627",
          "0628",
          "0631",
          "0632",
          "0633",
          "0701",
          "0702",
          "0704",
          "0706",
          "0709",
          "0710",
          "0711",
          "0712",
          "0713",
          "0714",
          "0715",
          "0716",
          "0719",
          "0720",
          "0722",
          "0723",
          "0728",
          "0729",
          "0805",
          "0806",
          "0807",
          "0811",
          "0814",
          "0815",
          "0817",
          "0819",
          "0821",
          "0822",
          "0826",
          "0827",
          "0828",
          "0829",
          "0830",
          "0831",
          "0833",
          "0834",
          "0901",
          "0904",
          "0906",
          "0911",
          "0912",
          "0914",
          "0919",
          "0926",
          "0928",
          "0929",
          "0935",
          "0937",
          "0938",
          "0940",
          "0941",
          "1001",
          "1002",
          "1003",
          "1004",
          "1014",
          "1017",
          "1018",
          "1021",
          "1026",
          "1027",
          "1029",
          "1032",
          "1034",
          "1037",
          "1046",
          "1101",
          "1102",
          "1103",
          "1106",
          "1111",
          "1112",
          "1114",
          "1119",
          "1120",
          "1121",
          "1122",
          "1124",
          "1127",
          "1129",
          "1130",
          "1133",
          "1134",
          "1135",
          "1141",
          "1142",
          "1144",
          "1145",
          "1146",
          "1149",
          "1151",
          "1160",
          "1201",
          "1211",
          "1216",
          "1219",
          "1221",
          "1222",
          "1223",
          "1224",
          "1227",
          "1228",
          "1231",
          "1232",
          "1233",
          "1234",
          "1235",
          "1238",
          "1241",
          "1242",
          "1243",
          "1244",
          "1245",
          "1246",
          "1247",
          "1251",
          "1252",
          "1253",
          "1256",
          "1259",
          "1260",
          "1263",
          "1264",
          "1265",
          "1266",
          "1401",
          "1411",
          "1412",
          "1413",
          "1416",
          "1417",
          "1418",
          "1419",
          "1420",
          "1421",
          "1422",
          "1424",
          "1426",
          "1428",
          "1429",
          "1430",
          "1431",
          "1432",
          "1433",
          "1438",
          "1439",
          "1441",
          "1443",
          "1444",
          "1445",
          "1449",
          "1502",
          "1504",
          "1505",
          "1511",
          "1514",
          "1515",
          "1516",
          "1517",
          "1519",
          "1520",
          "1523",
          "1524",
          "1525",
          "1526",
          "1528",
          "1529",
          "1531",
          "1532",
          "1534",
          "1535",
          "1539",
          "1543",
          "1545",
          "1546",
          "1547",
          "1548",
          "1551",
          "1554",
          "1557",
          "1560",
          "1563",
          "1566",
          "1567",
          "1571",
          "1573",
          "1576",
          "5001",
          "5004",
          "5005",
          "5011",
          "5012",
          "5013",
          "5014",
          "5015",
          "5016",
          "5017",
          "5018",
          "5019",
          "5020",
          "5021",
          "5022",
          "5023",
          "5024",
          "5025",
          "5026",
          "5027",
          "5028",
          "5029",
          "5030",
          "5031",
          "5032",
          "5033",
          "5034",
          "5035",
          "5036",
          "5037",
          "5038",
          "5039",
          "5040",
          "5041",
          "5042",
          "5043",
          "5044",
          "5045",
          "5046",
          "5047",
          "5048",
          "5049",
          "5050",
          "5051",
          "5052",
          "5053",
          "5054",
          "5061",
          "1601",
          "1612",
          "1613",
          "1617",
          "1620",
          "1621",
          "1622",
          "1624",
          "1627",
          "1630",
          "1632",
          "1633",
          "1634",
          "1635",
          "1636",
          "1638",
          "1640",
          "1644",
          "1648",
          "1653",
          "1657",
          "1662",
          "1663",
          "1664",
          "1665",
          "1702",
          "1703",
          "1711",
          "1714",
          "1717",
          "1718",
          "1719",
          "1721",
          "1724",
          "1725",
          "1736",
          "1738",
          "1739",
          "1740",
          "1742",
          "1743",
          "1744",
          "1748",
          "1749",
          "1750",
          "1751",
          "1755",
          "1756",
          "1804",
          "1805",
          "1811",
          "1812",
          "1813",
          "1815",
          "1816",
          "1818",
          "1820",
          "1822",
          "1824",
          "1825",
          "1826",
          "1827",
          "1828",
          "1832",
          "1833",
          "1834",
          "1835",
          "1836",
          "1837",
          "1838",
          "1839",
          "1840",
          "1841",
          "1845",
          "1848",
          "1849",
          "1850",
          "1851",
          "1852",
          "1853",
          "1854",
          "1856",
          "1857",
          "1859",
          "1860",
          "1865",
          "1866",
          "1867",
          "1868",
          "1870",
          "1871",
          "1874",
          "1902",
          "1903",
          "1911",
          "1913",
          "1917",
          "1919",
          "1920",
          "1922",
          "1923",
          "1924",
          "1925",
          "1926",
          "1927",
          "1928",
          "1929",
          "1931",
          "1933",
          "1936",
          "1938",
          "1939",
          "1940",
          "1941",
          "1942",
          "1943",
          "2002",
          "2003",
          "2004",
          "2011",
          "2012",
          "2014",
          "2015",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023",
          "2024",
          "2025",
          "2027",
          "2028",
          "2030",
          "2111"
        ]
      }
    },
    {
      "code": "ContentsCode",
      "selection": {
        "filter": "item",
        "values": [
          "KOSandel120000",
          "KOSandel150000",
          "KOSandel350000",
          "KOSbarnaav0000"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  kinderGartenAttendanceAndPersonnel_dataFrame = dataset.write('dataframe')
  kinderGartenAttendanceAndPersonnel_dataFrame.to_csv(dirname+'kinderGartenAttendanceAndPersonnel.csv')

  ##################################################  #################################################
  #03321: Employed persons (aged 15-74) per 4th quarter, by municipality of work, municipality of residence, contents and year
  print("Fetching SSB dataset: 03321: Employed persons (aged 15-74) per 4th quarter, by municipality of work, municipality of residence, contents and year")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/03321'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "ArbstedKomm",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "Bokommuen",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "ContentsCode",
      "selection": {
        "filter": "item",
        "values": [
          "Sysselsatte"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}


  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  municipalityResidenceEmployment_dataFrame = dataset.write('dataframe')
  municipalityResidenceEmployment_dataFrame.to_csv(dirname+'municipalityResidenceEmployment.csv')

  ####################################################################################################  #################################################
  #06445: Employed persons, by place of residence, sex and age (per cent). 4th quarter (M) 2005 - 2019
  print("Fetching SSB dataset: 06445: Employed persons, by place of residence, sex and age (per cent). 4th quarter (M) 2005 - 2019")

  POST_URL = 'https://data.ssb.no/api/v0/en/table/06445'

  # API query  - 
  payload = {
  "query": [
    {
      "code": "Region",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "Kjonn",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "Alder",
      "selection": {
        "filter": "all",
        "values": [
          "*"
        ]
      }
    },
    {
      "code": "ContentsCode",
      "selection": {
        "filter": "item",
        "values": [
          "Sysselsatte"
        ]
      }
    },
    {
      "code": "Tid",
      "selection": {
        "filter": "item",
        "values": [
          "2019"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}



  result = requests.post(POST_URL, json = payload)
  # Result gives only http status code - 200 if OK. Body comes in resultat.text
  print(result)

  dataset = pyjstat.Dataset.read(result.text)
  employementRate_dataFrame = dataset.write('dataframe')
  employementRate_dataFrame.to_csv(dirname+'employementRate.csv')

  ##################################################

  # #

  # POST_URL = 'https://data.ssb.no/api/v0/en/table/'

  # # API query  - 
  # payload = 

  # result = requests.post(POST_URL, json = payload)
  # # Result gives only http status code - 200 if OK. Body comes in resultat.text
  # print(result)

  # dataset = pyjstat.Dataset.read(result.text)
  # REPLACETHIS_dataFrame = dataset.write('dataframe')
  # REPLACETHIS_dataFrame.to_csv('REPLACETHIS.csv')

  #################################################

generateDemographicData()