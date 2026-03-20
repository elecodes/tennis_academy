# Google Sheets MCP Setup Guide

This guide explains how to set up the Google Sheets MCP server to allow AI agents to interact with your spreadsheets.

## Current Configuration

The project is configured to use:
- **Service Account**: `tennis-mcp-bot@sfcoachesschedule.iam.gserviceaccount.com`
- **Spreadsheet ID**: `1pnJWsdaALpM9NghSXM41O0yM29FMgXDCPgRnbbceQBU`
- **Key File**: `google-sheets-key.json` (in project root)

## Files

| File | Description |
|------|-------------|
| `google-sheets-key.json` | Service account credentials (gitignored) |
| `mcp_config.json` | MCP configuration |
| `.env` | Environment variables with spreadsheet ID |

## Configure OpenCode MCP

To enable the Google Sheets MCP in OpenCode, add this to your OpenCode config (`~/Downloads/opencode.json`):

```json
{
  "mcp": {
    "google-sheets": {
      "command": "uvx",
      "args": ["mcp-google-sheets"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/elena/Developer/tennis_academy/google-sheets-key.json"
      }
    }
  }
}
```

## Spreadsheet Access

Make sure the service account has access to your spreadsheet:
1. Open your Google Sheet
2. Click **Share**
3. Add: `tennis-mcp-bot@sfcoachesschedule.iam.gserviceaccount.com`
4. Give **Editor** access

## Troubleshooting

If the MCP isn't connecting:
1. Verify the service account has spreadsheet access
2. Check that `google-sheets-key.json` exists
3. Restart OpenCode after config changes
