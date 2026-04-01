import json


def make_mock_openai(response_dict: dict):
    """Returns a mock OpenAI client that returns response_dict as a chat completion."""
    content = json.dumps(response_dict)

    class _Resp:
        def __init__(self, c):
            self.choices = [type('choice', (), {
                'message': type('msg', (), {'content': c})()
            })()]

    class _Completions:
        def create(self, *args, **kwargs):
            return _Resp(content)

    class _Chat:
        completions = _Completions()

    class _Client:
        chat = _Chat()

    return _Client()
