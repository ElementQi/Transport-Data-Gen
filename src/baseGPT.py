from retrying import retry
import random
from openai import OpenAI


class BaseGPT:
    def __init__(
        self,
        model_name="deepseek-chat",
        keys_path=None,
        base_url="https://api.deepseek.com/v1",
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.client = None
        # save multiple keys to avoid rate limit
        with open(keys_path, encoding="utf-8", mode="r") as fr:
            self.keys = [line.strip() for line in fr if len(line.strip()) >= 4]

    def __post_process(self, response):
        return response.choices[0].message.content

    @retry(wait_fixed=200, stop_max_attempt_number=3)
    def __call__(self, system_prompt, prompt):
        if prompt is None or prompt == "":
            return False, "Your input is empty."

        current_key = random.choice(self.keys)
        self.client = OpenAI(api_key=current_key, base_url=self.base_url)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            top_p=0.8,
            frequency_penalty=0.6,
            presence_penalty=1,
            n=1,
        )

        return self.__post_process(response)


if __name__ == "__main__":
    gptGen = BaseGPT(keys_path="api_key.txt")
    text = "分类地球所有的州所在的半球"
    print(text)
    answer = gptGen("用json格式输出", text)
    print(answer)
