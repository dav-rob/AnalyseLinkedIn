import json

import jobchain.jc_logging as logging
import llm

from jobchain import JobABC
from sqlite_load import add_to_sqlite
from util.env_loader import get_env_key
from util.jinja_loader import get_jinja_prompt

logger = logging.getLogger(__name__)

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
        prompt_txt:str = generate_prompt(role)
        print(
                f"{counter}) --------------------------------------------------------------------------------------------------------------------------")
        counter += 1
        response = model.prompt(prompt_txt, temperature=0.7, system="You are an expert job description analyzer, " \
                                                                        "who writes a comprehensive description of job keywords.")
        add_analysis(response, role)

def jobchain_result_processor(result:dict):
    submitted_task = result.pop(JobABC.TASK_PASSTHROUGH_KEY)
    role = submitted_task["role"]
    if result.get("error"):
        logger.error(f"Error returned by LLM: {result['error']}")
        raise Exception(result['error'])
    llm_analysis = result["response"]
    add_analysis(llm_analysis, role)

def add_analysis(response, role):
    response_str = str(response)
    stripped_response = response_str.strip("`json")
    # print(stripped_response)
    analysis = deserialize_json_safely(stripped_response)
    role["analysis"] = analysis
    role_array = [role]
    add_to_sqlite(role_array)


def generate_prompt(role):
    role_desc = role["job_desc_txt"]
    example_json = load_example_json()
    prompt_txt = get_jinja_prompt("job_desc.txt", role_desc, example_json)
    return prompt_txt


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
        json_return = json.dumps(raw_string, indent=2)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {e}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise e
    return json_return


def get_error_json(e):
    error_message = str(e)
    #error_message = "Error deserializing json" #
    json_object = {
        "status": "error",
        "error": f"{{{error_message}}}"
    }
    return json_object
