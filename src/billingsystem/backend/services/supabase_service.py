import os
import uuid
from typing import List, Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class SupabaseService:
    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SECRET_API")
        
        if not supabase_url or not supabase_key:
            raise ValueError("missing variable SUPABASE_URL or SUPABASE_SECRET_API in .env")
            
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "recordings_screenshots"
        
    def get_client(self) -> Client:
        return self.client
        
    def insert_recording(self, user_id: str, started_at: str, ended_at: str, summary: str) -> str:
        data = {
            "user_id": user_id,
            "started_at": started_at,
            "ended_at": ended_at,
            "summary": summary
        }
        response = self.client.table("Recordings").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        raise Exception(f"Error with creating recording: {response}")

    def insert_frames(self, frames_data: List[Dict[str, Any]]):
        if not frames_data:
            return
            
        response = self.client.table("Frames").insert(frames_data).execute()
        return response.data

    def upload_screenshot(self, local_file_path: str, remote_file_name: str) -> str:
        with open(local_file_path, 'rb') as f:
            self.client.storage.from_(self.bucket_name).upload(
                path=remote_file_name,
                file=f,
                file_options={"content-type": "image/png"}
            )
            
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(remote_file_name)
        return public_url


