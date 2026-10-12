from ai_manager import call_gemini


class FakeResponse:
    text = ""


class FakeModel:
    def generate_content(self, **kwargs):
        return FakeResponse()


class FakeClient:
    models = FakeModel()


try:
    call_gemini(FakeClient(), "Test prompt")

except RuntimeError as e:
    print("Error handled successfully!")
    print(e)