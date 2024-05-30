from openai import OpenAI
key = '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'

client = OpenAI(api_key=key)
def generate_text(text):
    response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt=text,
    temperature=0.7,
    max_tokens=400
    )

    if response and response.choices:
      print(response.choices[0].text.strip())
      return response.choices[0].text.strip()
    else:
      print("Ошибка")
      return "Ошибка"


