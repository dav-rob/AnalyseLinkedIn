from jinja2 import Environment, FileSystemLoader

environment = Environment(loader=FileSystemLoader("templates"))

def get_jinja_prompt(jinja_file, job_desc, example_json):
    template = environment.get_template(jinja_file)
    content = template.render(
        job_description=job_desc,
        example_json_output=example_json
    )
    #print(f"*** Prompt is {content}")
    return content
