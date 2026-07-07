from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

credentials = Credentials(
    url="https://au-syd.ml.cloud.ibm.com",
    api_key="YOUR_API_KEY"
)

model = ModelInference(
    model_id="ibm/granite-3-2-8b-instruct",
    credentials=credentials,
    project_id="YOUR_PROJECT_ID"
)

print("SUCCESS")