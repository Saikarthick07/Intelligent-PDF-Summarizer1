import logging
import os
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import azure.durable_functions as df
from azure.identity import DefaultAzureCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from datetime import datetime
from openai import AzureOpenAI

# Create DFApp
my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Blob service client
blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("BLOB_STORAGE_ENDPOINT"))

# Blob trigger
@my_app.blob_trigger(arg_name="myblob", path="input", connection="BLOB_STORAGE_ENDPOINT")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    logging.info(f"Python blob trigger function processed blob "
                 f"Name: {myblob.name} "
                 f"Blob Size: {myblob.length} bytes")
    
    blobName = myblob.name.split("/")[1]
    await client.start_new("process_document", client_input=blobName)

# Orchestrator function
@my_app.orchestration_trigger(context_name="context")
def process_document(context):
    blobName: str = context.get_input()

    retry_options = df.RetryOptions(first_retry_interval_in_milliseconds=5000, max_number_of_attempts=3)

    result = yield context.call_activity_with_retry("analyze_pdf", retry_options, blobName)
    result2 = yield context.call_activity_with_retry("summarize_text", retry_options, result)
    result3 = yield context.call_activity_with_retry("write_doc", retry_options, {
        "blobName": blobName,
        "summary": result2
    })

    return logging.info(f"Successfully uploaded summary to {result3}")

# Analyze PDF Activity
@my_app.activity_trigger(input_name='blobName')
def analyze_pdf(blobName):
    logging.info("in analyze_text activity")
    container_client = blob_service_client.get_container_client("input")
    blob_client = container_client.get_blob_client(blobName)
    blob = blob_client.download_blob().readall()
    doc = ""

    endpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]
    credential = DefaultAzureCredential()

    document_analysis_client = DocumentAnalysisClient(endpoint, credential)
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=blob, locale="en-US")
    result = poller.result().pages

    for page in result:
        for line in page.lines:
            doc += line.content + " "

    return doc

# Summarize Text Activity (Azure OpenAI)
@my_app.activity_trigger(input_name='results')
def summarize_text(results):
    logging.info("in summarize_text activity")

    client = AzureOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        api_version="2024-02-15-preview",
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
    )

    prompt = f"Can you explain what the following text is about? {results}"

    response = client.chat.completions.create(
        model=os.environ["CHAT_MODEL_DEPLOYMENT_NAME"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response.choices[0].message.content
    logging.info(summary)
    return {"content": summary}

# Write Summary to Blob
@my_app.activity_trigger(input_name='results')
def write_doc(results):
    logging.info("in write_doc activity")
    container_client = blob_service_client.get_container_client("output")

    summary = results['blobName'] + "-" + str(datetime.now())
    sanitized_summary = summary.replace(".", "-")
    fileName = sanitized_summary + ".txt"

    logging.info("uploading to blob: " + results['summary']['content'])
    container_client.upload_blob(name=fileName, data=results['summary']['content'], overwrite=True)
    return fileName
