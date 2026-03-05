from anthropic import Anthropic

while True:
    p = input("write here: ")
    if p == "q":
        break
    client = Anthropic(api_key="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")  # Reads ANTHROPIC_API_KEY from environment
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"{p}"}],
    )
    print(f"\n{message.content}")