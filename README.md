
# Table Converter Azure Function for an Azure AI Search Skillset

This project provides an Azure Function app that exposes an HTTP API for converting tables (in Markdown or HTML) embedded in text into structured JSON. It is designed for use as a custom skill in Azure AI Search pipelines, but can also be run and tested locally.

## Features

- **/convert** endpoint: Accepts text containing Markdown or HTML tables, parses the tables, and replaces them with their JSON representation.
- Robust table parsing using `markdown-it-py` and `BeautifulSoup`.
- Pydantic models for strong input/output validation.
- Designed for Azure Functions, but can be run locally for development.

## How It Works

- **Input:** JSON payload with a `values` array, each containing a `recordId` and `data.text` field with the text to process.
- **Processing:** The `/convert` endpoint extracts tables from the text, converts them to JSON, and replaces the original table with a JSON code block.
- **Output:** JSON response with the same `recordId` and the processed text.

## Example Request

```json
POST /convert
Content-Type: application/json

{
  "values": [
    {
      "recordId": "0",
      "data": {
        "text": "Here is a table: | A | B |\n|---|---|\n| 1 | 2 |"
      }
    }
  ]
}
```

## Example Response

```json
{
  "values": [
    {
      "recordId": "0",
      "data": {
        "text": "Here is a table:\n```json\n[{\"A\":\"1\",\"B\":\"2\"}]\n```\n"
      },
      "errors": [],
      "warnings": []
    }
  ]
}
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── skill.py
│   └── routes/
│       ├── __init__.py
│       └── table_converter.py  # Main logic for table conversion
├── function_app.py             # Azure Functions entrypoint
├── requirements.txt            # Python dependencies
├── host.json                   # Azure Functions host configuration
├── local.settings.json         # Local Azure Functions settings (not committed)
├── tests/                      # HTTP request samples for local and Azure testing
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local) (for local development)
- (Recommended) Visual Studio Code with the [Azure Functions extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)

### Setup

1. **Clone the repository**

   ```pwsh
   git clone <your-repo-url>
   cd table-converter
   ```

2. **Create and activate a virtual environment**

   ```pwsh
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```pwsh
   pip install -r requirements.txt
   ```

4. **Run locally**

   ```pwsh
   func start
   ```

   The API will be available at `http://localhost:7071`.

5. **Test endpoints**

   You can use the sample HTTP files in the `tests` directory with the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) for VS Code, or use `curl`/Postman.

   Example:

   ```pwsh
   Invoke-RestMethod -Uri http://localhost:7071/convert -Method Post -ContentType 'application/json' -InFile .\tests\convert-test.http
   ```

### Debugging

- Use the provided VS Code launch configuration: **"Attach to Python Functions"**.
- This will start the function host and attach the debugger.

### Deployment

- Deploy to Azure using the Azure Functions extension or CLI.
- Make sure to set up your function app with a Python environment and deploy all files.

## Customization

- **Table parsing logic** is in `app/routes/table_converter.py`.
- **Skill interface models** are in `app/skill.py`.
- Adjust parsing or output formatting as needed for your use case.


## Add to Azure AI Search Skillset

The deployed function can be used in an Azure AI Search skillset when you use the `DocumentIntelligenceLayoutSkill` in a previous step.

```JSON
    {
      "@odata.type": "#Microsoft.Skills.Custom.WebApiSkill",
      "name": "JSON table converter",
      "description": "Converts tables in markdown to JSON.",
      "context": "/document/markdownDocument/*",
      "uri": "https://<func site>>.azurewebsites.net/convert",
      "httpMethod": "POST",
      "timeout": "PT3M50S",
      "batchSize": 10,
      "inputs": [
        {
          "name": "text",
          "source": "/document/markdownDocument/*/content",
          "inputs": []
        }
      ],
      "outputs": [
        {
          "name": "text",
          "targetName": "markdown_content"
        }
      ],
      "httpHeaders": {
        "x-functions-key": "<func key>"
      }
    },
```

