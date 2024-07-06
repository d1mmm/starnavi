import logging

import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
from vertexai.generative_models._generative_models import SafetyRating
from vertexai.preview import generative_models

from starnavi.config import CREDENTIALS, PROJECT_AI_ID

try:
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS)
    vertexai.init(project=PROJECT_AI_ID, location="us-central1", credentials=credentials)
except FileNotFoundError as e:
    logging.error(f"Error: The credentials file was not found. {e}")
except ValueError as e:
    logging.error(f"Error: Invalid credentials or project ID. {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")

model = GenerativeModel(model_name="gemini-1.5-flash-001")

generation_config = generative_models.GenerationConfig(
        max_output_tokens=100, temperature=0.4, top_p=1, top_k=32
    )

safety_config = [
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
    generative_models.SafetySetting(
        category=generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
        threshold=generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    )
]


def generate_answer(content, title=""):
    if title:
        contents = [title, content]
    else:
        contents = [content]

    response = model.generate_content(
        contents,
        generation_config=generation_config,
        safety_settings=safety_config,
    )
    return response


def analyze_content(content, title=""):
    response = generate_answer(content, title)
    result = next((severity for severity in response.candidates[0].safety_ratings if severity.severity !=
                   SafetyRating.HarmSeverity.HARM_SEVERITY_NEGLIGIBLE), None)
    if result:
        return False
    return True


def automatic_ai_answer(content, title=""):
    response = generate_answer(content, title)
    return response
