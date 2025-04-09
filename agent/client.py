from openai import OpenAI, AsyncOpenAI


class BaseClient(object):

    def __int__(self, api_key: str, base_url: str, model: str, *args, **kwargs):
        pass

    def chat_completion(self, message: str, stream: bool = False, extra_headers: dict = {}):
        pass


class DoubaoClient(BaseClient):

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def chat_completion(self, conversation: list, stream: bool = False, extra_headers: dict = {}):
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            extra_headers=extra_headers,
            stream=stream
        )
        return completion
