class MockLLMClient:
    def chat_completion(self, messages, json_mode=False):
        return '{"claims": []}' if json_mode else "Mock Report"
