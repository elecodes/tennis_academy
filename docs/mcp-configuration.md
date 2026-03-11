# Google Sheets MCP Setup Guide

This guide explains how to set up the Google Sheets MCP server to allow AI agents (like Antigravity) to interact with your spreadsheets.

## 1. Create Google Cloud Credentials

1.  Open the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a project (e.g., "Tennis Academy MCP").
3.  Go to **APIs & Services > Library** and search for "Google Sheets API". Click **Enable**.
4.  Go to **APIs & Services > Credentials**.
5.  Click **Create Credentials > Service Account**.
6.  Follow the prompts to create the account. No specific roles are required at this stage.
7.  Once created, click on the service account email, go to the **Keys** tab, and click **Add Key > Create new key**.
8.  Select **JSON** and download the file.
9.  Save this file inside your project directory as `service-account-key.json`. (Note: This file is already added to `.gitignore`).

## 2. Share your Spreadsheet

1.  Open the Google Spreadsheet you want the agent to access.
2.  Click the **Share** button.
3.  Copy the email address of your service account (from the JSON file) and paste it into the share box.
4.  Give it **Editor** permissions.

## 3. Configure the Agent

To use the MCP, you need to register it in your environment. If you are using Claude Desktop or another MCP-compatible client, add the following to your configuration:

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-google-sheets"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/absolute/path/to/tennis_academy/service-account-key.json"
      }
    }
  }
}
```

**Note**: Replace `/absolute/path/to/` with the actual path on your machine.
