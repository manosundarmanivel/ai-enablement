#!/usr/bin/env python3
"""
MCP Server for Presidio Insurance Documents
Provides insurance document search via Model Context Protocol
"""

import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google API setup
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDENTIALS_PATH = Path(__file__).parent / "credentials" / "service-account.json"

# MCP Server
server = Server("presidio-insurance-mcp")


def get_google_services():
    """Get Google Docs and Drive services."""
    creds = service_account.Credentials.from_service_account_file(
        str(CREDENTIALS_PATH),
        scopes=SCOPES,
    )
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    return docs_service, drive_service


def list_insurance_docs():
    """List all insurance documents from Google Drive."""
    _, drive = get_google_services()
    results = drive.files().list(
        q="mimeType='application/vnd.google-apps.document' and name contains 'Insurance'",
        fields="files(id, name, modifiedTime)",
    ).execute()
    return results.get("files", [])


def read_doc(doc_id: str) -> str:
    """Read content from a Google Doc."""
    docs, _ = get_google_services()
    document = docs.documents().get(documentId=doc_id).execute()
    content = document.get("body", {}).get("content", [])

    text = []
    for block in content:
        paragraph = block.get("paragraph")
        if not paragraph:
            continue
        for elem in paragraph.get("elements", []):
            run = elem.get("textRun")
            if run:
                text.append(run.get("content", ""))

    return "".join(text)


def extract_excerpt(text: str, keywords: list, context_chars: int = 300) -> str:
    """Extract relevant excerpt containing keywords."""
    text_lower = text.lower()

    best_pos = len(text)
    for kw in keywords:
        pos = text_lower.find(kw)
        if pos != -1 and pos < best_pos:
            best_pos = pos

    if best_pos == len(text):
        return text[:500].strip() + "..."

    start = max(0, best_pos - context_chars // 2)
    end = min(len(text), best_pos + context_chars)

    if start > 0:
        space_pos = text.find(" ", start)
        if space_pos != -1 and space_pos < best_pos:
            start = space_pos + 1

    if end < len(text):
        space_pos = text.rfind(" ", best_pos, end)
        if space_pos != -1:
            end = space_pos

    excerpt = text[start:end].strip()

    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."

    return excerpt


def search_docs(query: str) -> str:
    """Search insurance documents for a query."""
    docs = list_insurance_docs()

    if not docs:
        return "No insurance documents found in Google Drive."

    keywords = [kw.strip().lower() for kw in query.split() if len(kw.strip()) > 2]
    results = []

    for doc in docs:
        text = read_doc(doc["id"])
        text_lower = text.lower()

        match_count = 0
        matched_keywords = []
        for kw in keywords:
            if kw in text_lower:
                match_count += text_lower.count(kw)
                matched_keywords.append(kw)

        if matched_keywords:
            excerpt = extract_excerpt(text, matched_keywords)
            results.append({
                "title": doc["name"],
                "excerpt": excerpt,
                "relevance": match_count,
                "keywords": matched_keywords,
            })

    results.sort(key=lambda x: x["relevance"], reverse=True)

    if not results:
        return f"No insurance documents found matching: {query}"

    formatted = f"**Insurance Search Results for: '{query}'**\n\n"
    for r in results:
        formatted += f"### {r['title']}\n"
        formatted += f"**Matched:** {', '.join(r['keywords'])}\n"
        formatted += f"{r['excerpt']}\n\n"

    return formatted


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_insurance_docs",
            description="Search Presidio's Google Docs for insurance policy information including coverage limits, liability, cyber insurance, health benefits, and claims processes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query about insurance policies"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "search_insurance_docs":
        query = arguments.get("query", "")
        result = search_docs(query)
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
