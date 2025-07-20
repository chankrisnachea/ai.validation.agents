import requests

def build_prompt(description):
    return f"""
You are an AI assistant helping to extract test planning metadata from product requirements.

Requirement: "{description}"

Extract and return the following fields as JSON:
- domain: technical domain (e.g., power_management, artificial.intelligence, graphics, connectivity)
- interface: any interface mentioned (e.g., USB4, Type-C, PCIe)
- feature: core feature or function (e.g., tunneling, power gating)

Respond only with valid JSON:
"""

def extract_metadata_ollama(description):
    prompt = build_prompt(description)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt, "stream": False}
    )
    try:
        return response.json()["response"].strip()
    except Exception as e:
        print("Error:", e)
        return None

# Example use
print(extract_metadata_ollama("System must support USB4 tunneling over Type-C."))
