import os
import pathlib
import random


from string import Template
from .substitutions import Substitutions




class DataProcessing:

    def __init__(self, daphne_version='EOSS'):
        self.daphne_version = daphne_version
        self.sub_client = Substitutions(daphne_version)
        self.templates = self.load_templates()


    def load_templates(self):
        # cwd = os.getcwd()
        # curr_path = pathlib.Path(cwd)
        # root_path = pathlib.Path(*curr_path.parts[:-1])
        #
        # template_path = root_path / 'question_templates'
        # template_path = template_path / self.daphne_version
        #
        # data_path = root_path / 'data'
        # data_path = data_path / self.daphne_version

        template_path = '/app/daphne/command_classifier/question_templates/' + self.daphne_version
        data_path = '/app/daphne/command_classifier/data/' + self.daphne_version


        if not os.path.exists(data_path):
            os.makedirs(data_path)


        template_objects = []
        for filename in os.listdir(template_path):
            filepath = os.path.join(template_path, filename)

            # --> Load template object
            template_objects.append(self.load_template(filepath, filename, data_path))

        return template_objects

    def load_template(self, filepath, filename, datapath):

        # --> Parameters to extract from template
        question_class = int(filename.split('.', 1)[0])
        num_questions = 0
        parameter_map = {}
        labels = ""
        template_lines = []

        # --> Extract parameters
        with open(filepath, 'r') as file:
            state = 1
            for line in file:
                if line == '--\n':
                    state += 1
                else:
                    if state == 1:
                        num_questions = int(line[:-1])
                    elif state == 2:
                        line_info = line.split()
                        parameter_map[line_info[0]] = line_info[1]
                    elif state == 3:
                        labels = line[:-1]
                    elif state == 4:
                        template_lines.append(Template(line[:-1]))

        return {
            'num_questions': num_questions,
            'parameter_map': parameter_map,
            'labels': labels,
            'template_lines': template_lines,

            'file': filename,
            'path': filepath,
            'question_class': question_class,
            'outfile': os.path.join(datapath, filename)
        }


    def process(self):
        for qtemplate in self.templates:
            with open(qtemplate['outfile'], 'w') as file:
                file.write(qtemplate['labels'] + "\n")

                # --> Generate the random questions with substitutions
                for i in range(1, qtemplate['num_questions'] + 1):

                    # --> 1. Get a random substitution for each template parameter
                    params = {}
                    for param, param_type in qtemplate['parameter_map'].items():
                        params[param] = self.sub_client.get_substitution(param_type)

                    # --> 2. Get random template line for substitution
                    template_str = random.choice(qtemplate['template_lines'])

                    # --> 3. Substitute values into template line
                    question = template_str.substitute(params)
                    file.write(question + '\n')
