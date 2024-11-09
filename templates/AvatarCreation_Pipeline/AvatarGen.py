import requests

# Set up the URL and API key for OpenAI's DALL-E endpoint
url = "https://api.openai.com/v1/images/generations"
headers = {
    "Authorization": f"Bearer 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",
    "Content-Type": "application/json"
}

# Improved prompt for generating the cartoon avatar
data = {
    "prompt": (
        "A high-quality cartoon-style avatar of a friendly young person with curly brown hair, "
        "wearing stylish round glasses, smiling softly. The avatar should have a colorful, "
        "clean background (such as light blue or pastel colors) and feature detailed facial features "
        "with smooth lines and shading. The style should be modern and playful, with vibrant colors "
        "and soft lighting to give a friendly and approachable look. The character should be centered, "
        "from the shoulders up, and in a portrait orientation."
        "With a white background"
    ),
    "n": 1,
    "size": "1024x1024"
}

# Make the API request to generate the image
response = requests.post(url, headers=headers, json=data)

# Check if the request was successful and display the image URL
if response.status_code == 200:
    image_url = response.json()['data'][0]['url']
    print("Generated Image URL:", image_url)
else:
    print("Error:", response.json())
