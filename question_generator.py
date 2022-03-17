from string import Template
import os
import random
import pandas
from neo4j import GraphDatabase, basic_auth


def load_data_sources(daphne_version):
    if daphne_version == "EOSS":
        from db_client import Client, technologies

        # Connect to the database to retrieve names
        postgres_client = Client()

        return {
            "db_client": postgres_client,
            "technologies": technologies
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
            measurements = data_sources["db_client"].get_measurements()
            return random.choice(measurements)
        substitutions['measurement'] = subs_measurement

        def subs_technology(data_sources):
            technologies = list(data_sources["technologies"])
            for tech_type in data_sources["db_client"].get_instrument_types():
                technologies.append(tech_type)
            return random.choice(technologies)
        substitutions['technology'] = subs_technology

        def subs_mission(data_sources):
            missions = data_sources["db_client"].get_missions()
            return random.choice(missions)
        substitutions['mission'] = subs_mission

        def subs_agency(data_sources):
            agencies = data_sources["db_client"].get_agencies()
            return random.choice(agencies)
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
            objectives = data_sources["db_client"].get_objectives()
            return random.choice(objectives)
        substitutions['objective'] = subs_objective

        def subs_subobjective(data_sources):
            subobjectives = data_sources["db_client"].get_subobjectives()
            return random.choice(subobjectives)
        substitutions['subobjective'] = subs_subobjective

        def subs_not_partial_full(data_sources):
            options = ["not", "partially", "fully"]
            return random.choice(options)
        substitutions['not_partial_full'] = subs_not_partial_full

        def subs_agent(data_sources):
            options = ["expert", "historian", "analyst", "explorer", "engineer", "critic"]
            return random.choice(options)
        substitutions['agent'] = subs_agent

        def subs_orbit(data_sources):
            return random.randint(1, 5)
        substitutions['orbit'] = subs_orbit

        def subs_number(data_sources):
            return random.randint(1, 8)
        substitutions['number'] = subs_number

        def subs_instrument_parameter(data_sources):
            instrument_parameters = data_sources["db_client"].get_instrument_attributes()
            return random.choice(instrument_parameters)
        substitutions['instrument_parameter'] = subs_instrument_parameter

        def subs_vassar_instrument(data_sources):
            vassar_instruments = data_sources["db_client"].get_vassar_instruments()
            return random.choice(vassar_instruments)
        substitutions['vassar_instrument'] = subs_vassar_instrument

        def subs_vassar_measurement(data_sources):
            vassar_measurements = data_sources["db_client"].get_vassar_measurements()
            return random.choice(vassar_measurements)
        substitutions['vassar_measurement'] = subs_vassar_measurement

        def subs_vassar_stakeholder(data_sources):
            stakeholders = data_sources["db_client"].get_stakeholders()
            return random.choice(stakeholders)
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
