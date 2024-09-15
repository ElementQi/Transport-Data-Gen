from typing import Dict


class Template:
    def __init__(self, system: str, user: str):
        self.system = system
        self.user = user

    def format(self, **kwargs):
        return self.system, self.user.format(**kwargs)


TEMPLATES: Dict[str, Template] = {}


def _register_template(name: str, system: str = None, user: str = None) -> None:
    r"""
    Registers a data gen template.

    To add the following generation template:
    ```
    [SYSTEM]:
    system prompt here
    [USER]:
    user prompt here
    ```

    !!IMPORTANT!!
    You should make sure you let gpt generate the response in json format

    The corresponding code should be:
    ```
    _register_template(
        name="custom",
        system="system prompt here",
        user="user prompt here",
    )
    ```
    """
    TEMPLATES[name] = Template(system, user)


_register_template(
    name="evolution",
    system="""
    我希望你能扮演一个指令生成者。
    你的任务是从以下给定的问题和答案中获得灵感，生成一个全新的问题和相应的答案。
    这个新问题应属于同一个航空领域，但应更加罕见或长尾。
    新问题的长度和难度应与给定的问题相似，但是并不完全，一方面是要去掉一些无关信息，另外一方面需要正面回答，不要回答的太冗长。
    生成的新问题必须合理，且人类能够理解并作出回应。
    请不要在生成的新问题或答案中包含“给定问题”、“生成问题”、“given question”和“created question”。

    给定示例：
    问题：南航对无成人陪伴儿童的运输有什么特殊规定？
    答案：南航仅接受直达（不含经停）航班的无成人陪伴儿童的运输，这规定旨在减少儿童在旅行中的不确定性，确保他们的安全。

    根据以上示例生成一个新的问题和答案，并确保生成的格式如下：
    {
        "instruction": "生成的相关问题1",
        "output": "生成的相关背景1"
    }
    """,
    user="""
    给定以下问题和背景：
    问题：{instruction}
    答案：{output}
    
    输出必须为 JSON 格式，不要是 markdown 格式，包含 1 个新的 instruction 和 output。
    """,
)
