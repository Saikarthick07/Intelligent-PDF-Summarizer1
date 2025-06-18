# 🧠 Intelligent PDF Summarizer

This project is an AI-powered Azure Function App that automatically extracts and summarizes the content of uploaded PDF files using:

- **Azure Durable Functions** (Orchestration)
- **Azure Blob Storage** (Input/Output)
- **Azure Form Recognizer** (OCR & text extraction)
- **Azure OpenAI** (Summarization using GPT-3.5)
- **Python Runtime**

---

## ⚙️ Features

✅ Automatically triggered when a PDF is uploaded to Blob Storage  
✅ Extracts paragraphs using Form Recognizer  
✅ Summarizes content with GPT (OpenAI)  
✅ Saves output text file in the `output` container  
✅ Fully serverless and event-driven design

---

## 🚀 Architecture

```
PDF Upload → Blob Trigger Function →
  Durable Orchestrator →
    • ExtractTextActivity → Form Recognizer
    • SummarizeTextActivity → Azure OpenAI
    • SaveSummaryActivity → output container
```

---

## 🧪 Prerequisites

- Azure Subscription
- Python 3.9+
- Azure CLI
- Azure Functions Core Tools
- Azurite (optional for local dev)
- Virtual environment setup

---

## 🧰 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/Intelligent-PDF-Summarizer.git
cd Intelligent-PDF-Summarizer
```

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `local.settings.json`

Create a `local.settings.json` file:

```json
{
  "Values": {
    "AzureWebJobsStorage": "<your-storage-connection-string>",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "BLOB_STORAGE_ENDPOINT": "<same as storage connection string>",
    "COGNITIVE_SERVICES_ENDPOINT": "https://<your-form-recognizer>.cognitiveservices.azure.com/",
    "AZURE_OPENAI_ENDPOINT": "https://<your-openai-name>.openai.azure.com/",
    "AZURE_OPENAI_KEY": "<your-openai-key>",
    "CHAT_MODEL_DEPLOYMENT_NAME": "gpt-35-turbo"
  }
}
```

> ⚠️ Do not commit this file to GitHub. Add it to `.gitignore`.

---

## 🧪 Running the App Locally

```bash
func start
```

Upload a `.pdf` to the **`input`** container in your Blob Storage.  
The summarizer will:
- Extract text from the PDF
- Generate a summary
- Upload the summary `.txt` file to the **`output`** container

---

## ❗ Known Issues & Troubleshooting

### 1. **OpenAI Quota Limit**
Sometimes the summarization step failed due to **insufficient quota** on the Azure OpenAI resource.  
> ✅ Fix: Ensure that the deployed model has enough tokens and throughput for your workload.

### 2. **Blob Storage Connectivity**
The Azure Function intermittently failed to connect to the Blob Storage account, especially during local testing or missing `local.settings.json` setup.  
> ✅ Fix: Verify your `AzureWebJobsStorage` connection string and that the `input`/`output` containers exist.

---

## 📦 Deployment to Azure

1. Create an Azure Function App + Storage Account
2. Configure application settings in Azure Portal (use values from `local.settings.json`)
3. Publish:

```bash
func azure functionapp publish <your-app-name>
```

---

## 📺 Demo Video

Watch the full demo here: [📹 YouTube - Intelligent PDF Summarizer](https://youtu.be/us68soZ-beU)
