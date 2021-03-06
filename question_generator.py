from string import Template
import os
import random
import pandas
from neo4j import GraphDatabase, basic_auth


def load_data_sources(daphne_version):
    if daphne_version == "EOSS":
        from sqlalchemy.orm import sessionmaker
        import models
        from VASSARClient import VASSARClient

        # Connect to the database to retrieve names
        engine = models.db_connect()
        Session = sessionmaker(bind=engine)

        VASSAR = VASSARClient()

        instruments_sheet = pandas.read_excel('./xls/Climate-centric/Climate-centric AttributeSet.xls',
                                              sheet_name='Instrument')
        measurements_sheet = pandas.read_excel('./xls/Climate-centric/Climate-centric AttributeSet.xls',
                                               sheet_name='Measurement')
        param_names = []
        for row in measurements_sheet.itertuples(index=True, name='Measurement'):
            if row[2] == 'Parameter':
                for i in range(6, len(row)):
                    param_names.append(row[i])

        return {
            "vassar": VASSAR,
            "instruments_sheet": instruments_sheet,
            "param_names": param_names,
            "models": models,
            "session": Session()
        }

    if daphne_version == "EDL":
        return {}

    if daphne_version == "AT":
        # Setup neo4j database connection
        driver = GraphDatabase.driver("bolt://13.58.54.49:7687", auth=basic_auth("neo4j", "goSEAKers!"))
        session = driver.session()

        # Retrieve all the measurements
        query = 'MATCH (m:Measurement) RETURN DISTINCT m.Name'
        result = session.run(query)
        measurements_list = []
        for item in result:
            measurements_list.append(item[0])

        # Retrieve all the measurements' parameter groups
        query = 'MATCH (m:Measurement) RETURN DISTINCT m.ParameterGroup'
        result = session.run(query)
        parameter_groups_list = []
        for item in result:
            if item[0] is not None and item[0] != '':
                parameter_groups_list.append(item[0])
        print(parameter_groups_list)

        # Retrieve all the anomalies
        query = 'MATCH (a:Anomaly) RETURN DISTINCT a.Title'
        result = session.run(query)
        anomalies_list = []
        for item in result:
            anomalies_list.append(item[0])

        # Retrieve all the procedures
        query = 'MATCH (p:Procedure) RETURN DISTINCT p.Title'
        result = session.run(query)
        procedures_list = []
        for item in result:
            procedures_list.append(item[0])

        return {
            'measurements': measurements_list,
            'anomalies': anomalies_list,
            'procedures': procedures_list,
            'parameter_groups': parameter_groups_list
        }


def substitution_functions(daphne_version):
    # Define template substitutions depending on the type
    substitutions = dict()

    if daphne_version == "EOSS":
        def subs_measurement(data_sources):
            measurements = data_sources["session"].query(data_sources["models"].Measurement).all()
            return random.choice(measurements).name
        substitutions['measurement'] = subs_measurement

        def subs_technology(data_sources):
            technologies = list(data_sources["models"].technologies)
            for type in data_sources["session"].query(data_sources["models"].InstrumentType).all():
                technologies.append(type.name)
            return random.choice(technologies)
        substitutions['technology'] = subs_technology

        def subs_mission(data_sources):
            missions = data_sources["session"].query(data_sources["models"].Mission).all()
            return random.choice(missions).name
        substitutions['mission'] = subs_mission

        def subs_agency(data_sources):
            agencies = data_sources["session"].query(data_sources["models"].Agency).all()
            return random.choice(agencies).name
        substitutions['space_agency'] = subs_agency

        def subs_instrument_ifeed(data_sources):
            options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'j', 'k', 'l']
            return random.choice(options)
        substitutions['instrument'] = subs_instrument_ifeed

        def subs_year(data_sources):
            return random.randrange(1965, 2055)
        substitutions['year'] = subs_year

        def subs_design_id(data_sources):
            return "D" + str(random.randrange(1, 3000))
        substitutions['design_id'] = subs_design_id

        def subs_objective(data_sources):
            data_sources["vassar"].startConnection()
            objectives = data_sources["vassar"].client.getObjectiveList('ClimateCentric')
            data_sources["vassar"].endConnection()
            return random.choice(objectives)
        substitutions['objective'] = subs_objective

        def subs_subobjective(data_sources):
            data_sources["vassar"].startConnection()
            objectives = data_sources["vassar"].client.getSubobjectiveList('ClimateCentric')
            data_sources["vassar"].endConnection()
            return random.choice(objectives)
        substitutions['subobjective'] = subs_subobjective

        def subs_not_partial_full(data_sources):
            options = ["not", "partially", "fully"]
            return random.choice(options)
        substitutions['not_partial_full'] = subs_not_partial_full

        def subs_agent(data_sources):
            options = ["expert", "historian", "analyst", "explorer"]
            return random.choice(options)
        substitutions['agent'] = subs_agent

        def subs_orbit(data_sources):
            return random.randint(1, 5)
        substitutions['orbit'] = subs_orbit

        def subs_number(data_sources):
            return random.randint(1, 8)
        substitutions['number'] = subs_number

        def subs_instrument_parameter(data_sources):
            return random.choice(data_sources["instruments_sheet"]['Attributes-for-object-Instrument'])
        substitutions['instrument_parameter'] = subs_instrument_parameter

        def subs_vassar_instrument(data_sources):
            options = ["ACE_ORCA","ACE_POL","ACE_LID","CLAR_ERB","ACE_CPR","DESD_SAR","DESD_LID","GACM_VIS","GACM_SWIR",
                       "HYSP_TIR","POSTEPS_IRS","CNES_KaRIN","BIOMASS","SMAP_RAD","SMAP_MWR","CMIS","VIIRS"]
            return random.choice(options)
        substitutions['vassar_instrument'] = subs_vassar_instrument

        def subs_vassar_measurement(data_sources):
            return random.choice(data_sources["param_names"])
        substitutions['vassar_measurement'] = subs_vassar_measurement

        def subs_vassar_stakeholder(data_sources):
            options = ["Atmospheric", "Oceanic", "Terrestrial", "Weather", "Climate", "Land and ecosystems", "Water",
                       "Human health"]
            return random.choice(options)
        substitutions['vassar_stakeholder'] = subs_vassar_stakeholder

        return substitutions

    if daphne_version == "EDL":
        return substitutions

    if daphne_version == "AT":

        def subs_measurement(data_sources):
            options = data_sources['measurements']
            return random.choice(options)
        substitutions['measurement'] = subs_measurement

        def subs_anomaly(data_sources):
            options = data_sources['anomalies']
            return random.choice(options)
        substitutions['anomaly'] = subs_anomaly

        def subs_procedure(data_sources):
            options = data_sources['procedures']
            return random.choice(options)
        substitutions['procedure'] = subs_procedure

        def subs_parameter_group(data_sources):
            options = data_sources['parameter_groups']
            return random.choice(options)
        substitutions['parameter_group'] = subs_parameter_group

        return substitutions


if __name__ == '__main__':
    daphne_versions = ["EOSS"]  # "EDL", "AT"
    # Iterate over all types of questions
    for daphne_version in daphne_versions:
        data_sources = load_data_sources(daphne_version)
        substitutions = substitution_functions(daphne_version)
        templates_path = os.path.join(os.getcwd(), "question_templates", daphne_version)
        for filename in os.listdir(templates_path):
            question_class = int(filename.split('.', 1)[0])
            parameter_map = {}
            template_lines = []
            num_questions = 0
            labels = ""

            file_path = os.path.join(templates_path, filename)
            with open(file_path, 'r') as file:
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
            data_path = os.path.join(os.getcwd(), "data", daphne_version)
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            output_path = os.path.join(data_path, filename)
            with open(output_path, 'w') as file:
                file.write(labels + "\n")
                for i in range(1, num_questions+1):
                    # Generate a set of parameters
                    params = {}
                    for param, param_type in parameter_map.items():
                        params[param] = substitutions[param_type](data_sources)

                    # Generate a question
                    template = random.choice(template_lines)
                    question = template.substitute(params)
                    file.write(question + '\n')
                    print(question)
