import azure.functions as func
import pandas as pd
import io
import json
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

bp1 = func.Blueprint()

@bp1.route(route="GetRandomRecords", methods=["POST"])
def get_random_records(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Auth via Managed Identity
    token_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url="https://meenafuncappsource.blob.core.windows.net", 
        credential=token_credential
    )

    try:
        # 2. Read from Blob
        blob_client = blob_service_client.get_blob_client(container="input", blob="Sample Data - Meena.xlsx")
        data = blob_client.download_blob().readall()
        df = pd.read_excel(io.BytesIO(data))

        # 3. Process: 3 random records per Category/Sub category
        sampled_df = df.groupby(['category', 'sub_category']).apply(
            lambda x: x.sample(n=min(len(x), 3))
        ).reset_index(drop=True)

        # 4. Filter columns and convert to JSON
        result = sampled_df[['id', 'text']].to_dict(orient='records')
        
        # 5. Write back to Blob
        output_client = blob_service_client.get_blob_client(container="output", blob="random_records.json")
        output_client.upload_blob(json.dumps(result), overwrite=True)

        return func.HttpResponse("JSON generated successfully.", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
    