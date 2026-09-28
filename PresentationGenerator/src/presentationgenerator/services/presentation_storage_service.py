"""
Service for saving and retrieving presentations from Supabase.
"""

import os
from fastapi import HTTPException
from supabase import create_client, Client
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

TABLE = "presentations"


def _get_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


class PresentationStorageService:

    def save(self, user_id: str, topic: str, html: str, slides_count: int) -> dict:
        """
        Saves a generated presentation to the database.

        :param user_id:     UUID of the authenticated user.
        :param topic:       Presentation topic / title.
        :param html:        Full HTML string of the presentation.
        :param slides_count: Number of slides.
        :return:            The inserted row as a dict.
        """
        supabase = _get_client()
        try:
            response = (
                supabase.table(TABLE)
                .insert({
                    "user_id": user_id,
                    "topic": topic,
                    "html": html,
                    "slides_count": slides_count,
                })
                .execute()
            )
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to save presentation.")
            return response.data[0]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e

    def get_all_for_user(self, user_id: str) -> list[dict]:
        """
        Returns all presentations belonging to the given user,
        ordered from newest to oldest. HTML is excluded to keep
        the list response lightweight.

        :param user_id: UUID of the authenticated user.
        :return:        List of presentation rows (without the html field).
        """
        supabase = _get_client()
        try:
            response = (
                supabase.table(TABLE)
                .select("id, user_id, topic, slides_count, created_at")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e

    def get_by_id(self, presentation_id: str, user_id: str) -> dict:
        """
        Returns a single presentation by its ID, including full HTML.
        Raises 404 if not found or if it belongs to a different user.

        :param presentation_id: UUID of the presentation row.
        :param user_id:         UUID of the authenticated user (ownership check).
        :return:                Full presentation row as a dict.
        """
        supabase = _get_client()
        try:
            response = (
                supabase.table(TABLE)
                .select("*")
                .eq("id", presentation_id)
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            if not response.data:
                raise HTTPException(status_code=404, detail="Presentation not found.")
            return response.data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=404, detail="Presentation not found.") from e
