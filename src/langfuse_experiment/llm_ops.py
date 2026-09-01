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


def publish_dataset(langfuse, dataset_name):
    try:
        with (
            resources.files("datasets")
            .joinpath("{}.yaml".format(dataset_name))
            .open("r") as f
        ):
            # TODO: Map to a struct, validate required fields
            dataset_dic = yaml.safe_load(f)
            print(dataset_dic)

            name = dataset_dic["name"]
            description = dataset_dic["description"]
            items = dataset_dic["items"]

            langfuse.create_dataset(
                name=name,
                description=description,
            )

            [
                langfuse.create_dataset_item(
                    dataset_name=name,
                    input=i["input"],
                    expected_output=i["expected_output"],
                    metadata=i["metadata"],
                )
                for i in items
            ]

    except Exception as e:
        print(e)
