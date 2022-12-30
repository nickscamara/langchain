"""NotionAPI to save document.

"""
import os
import sys
from typing import Any, Dict, Optional

from pydantic import BaseModel, Extra, root_validator

from langchain.utils import get_from_dict_or_env


class NotionAPIWrapper(BaseModel):
    """Wrapper around Notion API.

    # TODO: docs

    """

    notion_client: Any  #: :meta private:

    notion_token: Optional[str] = None
    notion_database_id: Optional[str] = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        notion_token = get_from_dict_or_env(values, "notion_token", "NOTION_TOKEN")
        values["NOTION_TOKEN"] = notion_token
        notion_database_id = get_from_dict_or_env(
            values, "notion_database_id", "NOTION_DATABASE_ID"
        )
        values["NOTION_DATABASE_ID"] = notion_database_id

        try:
            from notion_client import Client

            values["notion_client"] = Client

        except ImportError:
            raise ValueError(
                "Could not import serpapi python package. "
                "Please it install it with `pip install notion-client`."
            )
        return values

    def _write_to_notion(self, notion_client, document: str, document_title: str):
        parent = {"database_id": self.notion_database_id}
        properties = {"Name": {"title": [{"type": "text", "text": {"content": document_title}}]}}
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": document}}]
                },
            }
        ]
        try:
            notion_client.pages.create(
                parent=parent, properties=properties, children=children
            )
            return "Wrote to Notion successfully!"

        except Exception as e:
            return "Failed to write to Notion. Here is the exception message: " + str(e)

    def run(self, document: str) -> str:
        """Run query through SerpAPI and parse result."""
        params = {"auth": self.notion_token}
        notion_client = self.notion_client(params)
        print("Document")
        print(document)
        return self._write_to_notion(notion_client, document,document[0:10] + "...")

