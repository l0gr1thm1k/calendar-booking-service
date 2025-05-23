class LLMChatError(ValueError):
    def __init__(self, message="An error occurred when chatting with the LLM."):
        self.message = message
        super().__init__(self.message)
