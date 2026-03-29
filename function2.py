import azure.functions as func
import pandas as pd
import io
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

bp2 = func.Blueprint()

@bp2.route(route="FilterByDate", methods=["POST"])
def filter_by_date(req: func.HttpRequest) -> func.HttpResponse:
    token_credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url="https://functionappsrc.blob.core.windows.net", 
        credential=token_credential
    )

    try:
        blob_client = blob_service_client.get_blob_client(container="input", blob="meenasample.xlsx")
        data = blob_client.download_blob().readall()
        df = pd.read_excel(io.BytesIO(data))

        # Filter Date > 1st Oct 2025
        df['Date'] = pd.to_datetime(df['Date'])
        filtered_df = df[df['Date'] > '2026-03-07']

        # Save as Excel in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        
        # Upload
        output_client = blob_service_client.get_blob_client(container="output", blob="filtered.xlsx")
        output_client.upload_blob(output.getvalue(), overwrite=True)

        return func.HttpResponse("Filtered Excel uploaded.", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)