import json

import llm

from util.env_loader import get_env_key
from util.jinja_loader import get_jinja_prompt


def analyse_role_desc(role_array):
    api_key = get_env_key('OPENAI_API_KEY')
    # gpt-4o context length is 128,000
    #   its default maximum number of output tokens (completion tokens) is typically limited to 4,096 tokens
    model = llm.get_model("gpt-4o")
    model.key = api_key
    counter = 1
    for role in role_array:
    # for i in range(4):
    #     role = role_array[i]
        role_desc = role["job_desc_txt"]
        example_json = load_example_json()
        prompt_txt = get_jinja_prompt("job_desc.txt", role_desc, example_json)
        print(
            f"{counter}) --------------------------------------------------------------------------------------------------------------------------")
        counter += 1
        response = model.prompt(prompt_txt, temperature=0.7, system="You are an expert job description analyzer, " \
                                                                    "who writes a comprehensive description of job keywords.")
        response_str = str(response)
        stripped_response = response_str.strip("`json")
        #print(stripped_response)
        analysis = deserialize_json_safely(stripped_response)
        role["analysis"] = analysis


def load_example_json():
    # with open('templates/example.json', 'r') as f:
    #     example_json = json.load(f)
    #     return example_json
    with open('templates/example.txt', 'r') as file:  # this file is not well formatted json so it is .txt
        example_json = file.read()
        return example_json


def deserialize_json_safely(raw_string):
    """
    Method makes sure that if the JSON deserializing is going to throw an error because of badly formatted
    json string then the whole process does not crash out.

    :param raw_string:
    :return:
    """
    try:
        json_return = json.loads(raw_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        json_return = get_error_json(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        json_return = get_error_json(e)
    return json_return


def get_error_json(e):
    error_message = str(e)
    #error_message = "Error deserializing json" #
    json_object = {
        "status": "error",
        "error": f"{{{error_message}}}"
    }
    return json_object
