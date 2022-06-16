import os



q_template_path = '/app/daphne/command_classifier/question_templates/EOSS2'


def get_file_list():
    file_list = []
    for x in range(2020, 2063):
        file_list.append(str(x))
    return file_list



def rename():
    print('--> FORMATTING')

    file_list = get_file_list()
    print(file_list)

    files_to_change = []

    sorted_files = os.listdir(q_template_path)
    sorted_files.sort()
    for filename in sorted_files:
        if filename.endswith(".txt"):
            file_number = filename[:-4]
            if file_number in file_list:
                files_to_change.append(os.path.join(q_template_path, filename))


    start_count = 5000
    for count, filename in enumerate(files_to_change):
        new_name = str(start_count + count) + '.txt'
        new_file = os.path.join(q_template_path, new_name)
        os.rename(filename, new_file)





def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def get_label_line(filepath, filename):
    # --> Parameters to extract from template
    question_class = int(filename.split('.', 1)[0])
    num_questions = 0
    parameter_map = {}
    labels = ""
    template_lines = []

    # --> Extract parameters
    with open(filepath, 'r') as file:
        state = 1
        for line_num, line in enumerate(file):
            if line == '--\n':
                state += 1
            else:
                if state == 1:
                    num_questions = int(line[:-1])
                elif state == 2:
                    line_info = line.split()
                    parameter_map[line_info[0]] = line_info[1]
                elif state == 3:
                    return line_num
    return -1



def identifier():
    print('--> CHANGING FILE IDENTIFIER')

    for filename in os.listdir(q_template_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(q_template_path, filename)
            label_line = get_label_line(file_path, filename)

            file_ident = int(filename[0])
            file_label = '-1'
            if file_ident == 1:
                file_label = '10000'
            elif file_ident == 2:
                file_label = '01000'
            elif file_ident == 3:
                file_label = '00100'
            elif file_ident == 4:
                file_label = '00010'
            elif file_ident == 5:
                file_label = '00001'
            file_label += '\n'

            replace_line(file_path, label_line, file_label)




template_path = '/app/daphne/daphne_brain/EOSS/dialogue/command_types/Teacher'



def rename2():
    files_to_change = []
    for filename in os.listdir(template_path):
        if filename.endswith(".json"):
            file_number = filename[:-4]
            files_to_change.append(filename)

    start_count = 5000
    for count, filename in enumerate(files_to_change):
        new_name = str(start_count + count) + '.json'
        new_file = os.path.join(template_path, new_name)
        os.rename(os.path.join(template_path, filename), new_file)




def generate_teacher_qtypes():
    print('--> GENERATING TEACHER QUESTION TYPES')



    starting_num = 5000
    for x in range(43):
        file_num = starting_num + x
        file_name = str(file_num) + '.json'
        file_path = os.path.join(template_path, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        file_template = '''{{
  "type": "run_function",
  "params": [],
  "objective": "return a definition",
  "function":
  {{
    "run_template": "dialogue_functions.definitions.get_definition_{file_number}()",
    "results": [
      {{
        "result_type": "single",
        "result_fields": {{
          "text_response": "command_results[0]"
        }}
      }}
    ]
  }},
  "voice_response": [
    {{
      "type": "single",
      "template": "${{text_response}}"
    }}
  ],
  "visual_response": [
    {{
      "type": "text",
      "from": "single",
      "template": "${{text_response}}"
    }}
  ]
}}'''.format(file_number=file_num)
        with open(file_path, 'w') as file:
            file.write(file_template)












if __name__ == '__main__':
    generate_teacher_qtypes()