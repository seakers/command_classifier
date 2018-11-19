from string import Template
import os
import random
from sqlalchemy.orm import sessionmaker
import models
from VASSARClient import VASSARClient
import pandas

# Connect to the database to retrieve names
engine = models.db_connect()
Session = sessionmaker(bind=engine)

VASSAR = VASSARClient()

instruments_sheet = pandas.read_excel('./xls/Climate-centric/Climate-centric AttributeSet.xls', sheet_name='Instrument')
measurements_sheet = pandas.read_excel('./xls/Climate-centric/Climate-centric AttributeSet.xls', sheet_name='Measurement')
param_names = []
for row in measurements_sheet.itertuples(index=True, name='Measurement'):
    if row[2] == 'Parameter':
        for i in range(6, len(row)):
            param_names.append(row[i])

# Define template substitutions depending on the type
substitutions = dict()


def subs_measurement(session):
    measurements = session.query(models.Measurement).all()
    return random.choice(measurements).name


def subs_technology(session):
    technologies = list(models.technologies)
    for type in session.query(models.InstrumentType).all():
        technologies.append(type.name)
    return random.choice(technologies)


def subs_mission(session):
    missions = session.query(models.Mission).all()
    return random.choice(missions).name


def subs_agency(session):
    agencies = session.query(models.Agency).all()
    return random.choice(agencies).name


def subs_instrument_ifeed(session):
    options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'j', 'k', 'l']
    return random.choice(options)


def subs_year(session):
    return random.randrange(1965, 2055)


def subs_design_id(session):
    return "D" + str(random.randrange(1, 3000))


def subs_objective(session):
    VASSAR.startConnection()
    objectives = VASSAR.client.getObjectiveList('ClimateCentric')
    VASSAR.endConnection()
    return random.choice(objectives)


def subs_not_partial_full(session):
    options = ["not", "partially", "fully"]
    return random.choice(options)


def subs_agent(session):
    options = ["expert", "historian", "analyst", "explorer"]
    return random.choice(options)


def subs_orbit(session):
    return random.randint(1, 5)


def subs_number(session):
    return random.randint(1, 8)


def subs_instrument_parameter(session):
    return random.choice(instruments_sheet['Attributes-for-object-Instrument'])


def subs_vassar_instrument(session):
    options = ["ACE_ORCA","ACE_POL","ACE_LID","CLAR_ERB","ACE_CPR","DESD_SAR","DESD_LID","GACM_VIS","GACM_SWIR",
               "HYSP_TIR","POSTEPS_IRS","CNES_KaRIN","BIOMASS","SMAP_RAD","SMAP_MWR","CMIS","VIIRS"]
    return random.choice(options)


def subs_vassar_measurement(session):
    return random.choice(param_names)


def subs_vassar_stakeholder(session):
    options = ["Atmospheric", "Oceanic", "Terrestrial", "Weather", "Climate", "Land and ecosystems", "Water",
               "Human health"]
    return random.choice(options)


substitutions['measurement'] = subs_measurement
substitutions['technology'] = subs_technology
substitutions['mission'] = subs_mission
substitutions['instrument'] = subs_instrument_ifeed
substitutions['space_agency'] = subs_agency
substitutions['year'] = subs_year
substitutions['design_id'] = subs_design_id
substitutions['objective'] = subs_objective
substitutions['not_partial_full'] = subs_not_partial_full
substitutions['agent'] = subs_agent
substitutions['orbit'] = subs_orbit
substitutions['number'] = subs_number
substitutions['instrument_parameter'] = subs_instrument_parameter
substitutions['vassar_instrument'] = subs_vassar_instrument
substitutions['vassar_measurement'] = subs_vassar_measurement
substitutions['vassar_stakeholder'] = subs_vassar_stakeholder


# Iterate over all types of questions
for filename in os.listdir('./question_templates'):
    question_class = int(filename.split('.', 1)[0])
    parameter_map = {}
    template_lines = []
    num_questions = 0
    labels = ""
    session = Session()

    with open('./question_templates/' + filename, 'r') as file:
        state = 1
        for line in file:
            if line == '--\n':
                state += 1
            else:
                if state == 1:
                    # Set number of questions
                    num_questions = int(line[:-1])
                elif state == 2:
                    # Add to list of variables
                    line_info = line.split()
                    parameter_map[line_info[0]] = line_info[1]
                elif state == 3:
                    # Add to list of templates
                    labels = line[:-1]
                elif state == 4:
                    # Add to list of templates
                    template_lines.append(Template(line[:-1]))


    # Start generating random questions
    if not os.path.exists('./data'):
        os.makedirs('./data')
    with open('./data/' + filename, 'w') as file:
        file.write(labels + "\n")
        for i in range(1, num_questions+1):
            # Generate a set of parameters
            params = {}
            for param, type in parameter_map.items():
                params[param] = substitutions[type](session)

            # Generate a question
            template = random.choice(template_lines)
            question = template.substitute(params)
            file.write(question + '\n')
            print(question)