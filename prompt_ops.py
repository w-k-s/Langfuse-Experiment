from importlib import resources
import yaml


def publish_prompt(langfuse, prompt_name):
    try:
        with (
            resources.files("prompts")
            .joinpath("{}.yaml".format(prompt_name))
            .open("r") as f
        ):
            # TODO: Map to a struct, validate required fields
            prompt_dic = yaml.safe_load(f)
            print(prompt_dic)
            langfuse.create_prompt(**prompt_dic)
    except Exception as e:
        print(e)
