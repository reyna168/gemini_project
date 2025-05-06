from google import genai

GOOGLE_API_KEY = ""
client = genai.Client(api_key=GOOGLE_API_KEY)

response = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")