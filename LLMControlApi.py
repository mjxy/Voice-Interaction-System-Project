from openai import OpenAI


class LLMControlApi:
    def __init__(self, api_key, base_url, filename="Prompt.txt"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.prompt = self.get_prompt_from_txt(filename)

    def get_prompt_from_txt(self, file_path):
        """
        Get the prompt from the txt file path.
        :param file_path: The path of the txt file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None

    def get_model_feedback(self, user_input):
        """
        Get the feedback result from the large language model.
        :param user_input: The user input.
        :return: The model feedback result, in string type.
        """
        if self.client is None or self.prompt is None:
            raise ValueError("You need to add the Baseurl, API key and get the prompt first to get the feedback.")

        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_input}
        ]

        completion = self.client.chat.completions.create(
            model="ep-20250227141841-6nlvh",
            messages=messages
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    # Replace with your own real API key and Baseurl
    LLM_api_key = "xxx"
    LLM_base_url = "xxx"
    LLM_filename = "Prompt.txt"

    voice_model = LLMControlApi(LLM_api_key, LLM_base_url, LLM_filename)

    user_input = "Raise the step height to 15cm"
    # Get the model feedback result
    result = voice_model.get_model_feedback(user_input)
    print(result)