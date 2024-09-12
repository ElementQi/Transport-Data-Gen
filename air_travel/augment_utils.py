import json

# ---- INSTRUCTION EVOLUTION ----

def in_breadth_evolving_prompt(entry, idx, client):
    instruction = entry['instruction']
    output = entry['output']
    
    # In-Breadth Evolving
    evolving_prompt = """
    我希望你能扮演一个指令生成者。
    你的任务是从以下给定的问题和答案中获得灵感，生成一个全新的问题和相应的答案。
    这个新问题应属于同一个航空领域，但应更加罕见或长尾。
    新问题的长度和难度应与给定的问题相似。
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
    """

    prompt = f"""
    给定以下问题和背景：
    问题：{instruction}
    答案：{output}
    
    输出必须为 JSON 格式，不要是 markdown 格式，包含 1 个新的 instruction 和 output。
    """


    try:
        response = client.chat.completions.create(
            model="Qwen2-72B-Instruct-GPTQ-Int8",
            messages=[
                {"role": "system", "content": evolving_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        json_response = json.loads(response.choices[0].message.content)
        
        return json_response
    
    except Exception as e:
        print(f"Error generating entry {idx}: {str(e)}")


def evolution(data, idx_all_data, client):
    new_data = []
    
    for idx, entry in enumerate(data):
        result = in_breadth_evolving_prompt(data, idx_all_data, client)
        if result:
            new_data.append(result)
        
        if len(new_data) >= 4:
            break

    return new_data



# ---- original instruction ----

def default(entry, idx, client):
    new_entries = []
    instruction = entry['instruction']
    output = entry['output']
    
    system_prompt = """
    你是一个有帮助的助手。你的任务是基于给定的输入问题和背景，生成 4 个新的问题和相应的背景，输出必须为 JSON 格式，格式如下：
    [
      {
        "instruction": "生成的相关问题1",
        "output": "生成的相关背景1"
      },
      {
        "instruction": "生成的相关问题2",
        "output": "生成的相关背景2"
      },
      {
        "instruction": "生成的相关问题3",
        "output": "生成的相关背景3"
      },
      {
        "instruction": "生成的相关问题4",
        "output": "生成的相关背景4"
      }
    ]
    你应该根据背景的内容生成问题，如果背景过长，可以自行分割并生成问题和相应的背景。
    """

    prompt = f"""
    给定以下问题和背景：
    问题：{instruction}
    背景：{output}
    
    请根据内容生成 4 个相关的新的问题和背景，确保每个问题与背景内容高度相关，且避免重复。
    输出必须为 JSON 格式，不要是 markdown 格式，包含 4 个新的 instruction 和 output。
    """

    try:
        response = client.chat.completions.create(
            model="Qwen2-72B-Instruct-GPTQ-Int8",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        json_response = json.loads(response.choices[0].message.content)

        # make sure as expected(4 new instruction-output pairs)
        if isinstance(json_response, list) and len(json_response) >= 4:
            new_entries.extend(json_response)
        else:
            print(f"Unexpected format at index {idx}: {json_response}")

    except Exception as e:
        print(f"Error generating entry {idx}: {str(e)}")
    
    return new_entries

