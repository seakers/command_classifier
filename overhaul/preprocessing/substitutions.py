from string import Template
import os
import random
import pandas
from .db_client import Client, technologies






class Substitutions:

    def __init__(self, daphne_version):
        self.daphne_version = daphne_version

        self.db_client = Client()
        self.technologies = technologies


        # --> Build Substitutions
        self.substitutions = dict()
        self.substitutions['cost_element'] = self.subs_cost_element
        self.substitutions['measurement'] = self.subs_measurement
        self.substitutions['mission'] = self.subs_mission
        self.substitutions['space_agency'] = self.subs_agency
        self.substitutions['instrument'] = self.subs_instrument_ifeed
        self.substitutions['year'] = self.subs_year
        self.substitutions['design_id'] = self.subs_design_id
        self.substitutions['objective'] = self.subs_objective
        self.substitutions['subobjective'] = self.subs_subobjective
        self.substitutions['not_partial_full'] = self.subs_not_partial_full
        self.substitutions['agent'] = self.subs_agent
        self.substitutions['orbit'] = self.subs_orbit
        self.substitutions['number'] = self.subs_number
        self.substitutions['instrument_parameter'] = self.subs_instrument_parameter
        self.substitutions['vassar_instrument'] = self.subs_vassar_instrument
        self.substitutions['vassar_measurement'] = self.subs_vassar_measurement
        self.substitutions['vassar_stakeholder'] = self.subs_vassar_stakeholder
        self.substitutions['technology'] = self.subs_technology


    def get_substitution(self, wildcard):
        if wildcard not in self.substitutions:
            print('--> NO SUBSTITUTION FOUND FOR WILDCARD:', wildcard)
            return None
        return self.substitutions[wildcard]()


    """
      _____         _       ______                    _    _                    
     / ____|       | |     |  ____|                  | |  (_)                   
    | (___   _   _ | |__   | |__  _   _  _ __    ___ | |_  _   ___   _ __   ___ 
     \___ \ | | | || '_ \  |  __|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
     ____) || |_| || |_) | | |   | |_| || | | || (__ | |_ | || (_) || | | |\__ \
    |_____/  \__,_||_.__/  |_|    \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
                                                                                                          
    """

    def subs_cost_element(self):
        cost_elements = [
            'launch-cost', 'bus-cost', 'bus-recurring-cost', 'bus-non-recurring-cost', 'payload-cost',
            'payload-recurring-cost', 'payload-non-recurring-cost', 'satellite-cost', 'spacecraft-recurring-cost',
            'spacecraft-non-recurring-cost',
            'IAT-cost', 'IAT-recurring-cost', 'IAT-non-recurring-cost', 'program-cost', 'program-recurring-cost',
            'program-non-recurring-cost', 'operations-cost', 'mission-recurring-cost', 'mission-non-recurring-cost',
            'lifecycle-cost'
        ]
        return random.choice(cost_elements)



    def subs_measurement(self):
        measurements = self.db_client.get_measurements()
        return random.choice(measurements)



    def subs_technology(self):
        technologies = list(self.technologies)
        for tech_type in self.db_client.get_instrument_types():
            technologies.append(tech_type)
        return random.choice(technologies)



    def subs_mission(self):
        missions = self.db_client.get_missions()
        return random.choice(missions)


    def subs_agency(self):
        agencies = self.db_client.get_agencies()
        return random.choice(agencies)


    def subs_instrument_ifeed(self):
        options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'j', 'k', 'l']
        return random.choice(options)


    def subs_year(self):
        return random.randrange(1965, 2055)


    def subs_design_id(self):
        return "D" + str(random.randrange(1, 3000))


    def subs_objective(self):
        objectives = self.db_client.get_objectives()
        return random.choice(objectives)


    def subs_subobjective(self):
        subobjectives = self.db_client.get_subobjectives()
        return random.choice(subobjectives)


    def subs_not_partial_full(self):
        options = ["not", "partially", "fully"]
        return random.choice(options)


    def subs_agent(self):
        options = ["expert", "historian", "analyst", "explorer", "engineer", "critic"]
        return random.choice(options)


    def subs_orbit(self):
        return random.randint(1, 5)


    def subs_number(self):
        return random.randint(1, 8)


    def subs_instrument_parameter(self):
        instrument_parameters = self.db_client.get_instrument_attributes()
        return random.choice(instrument_parameters)


    def subs_vassar_instrument(self):
        vassar_instruments = self.db_client.get_vassar_instruments()
        return random.choice(vassar_instruments)


    def subs_vassar_measurement(self):
        vassar_measurements = self.db_client.get_vassar_measurements()
        return random.choice(vassar_measurements)


    def subs_vassar_stakeholder(self):
        stakeholders = self.db_client.get_stakeholders()
        return random.choice(stakeholders)









































"""
    This function returns a dictionary with the following key-value pairs
    --- key: label indicating wildcard type in sting to be classified
    - value: a function purposed to generate a random wildcard value for the label, takes data_sources as parameter

"""






