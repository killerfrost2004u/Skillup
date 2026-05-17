import os
import requests
from datetime import datetime
from ..data.repository import CourseRepository, UserRepository

class CourseService:
    @staticmethod
    def get_all_courses():
        return CourseRepository.get_all()

    @staticmethod
    def get_user_progress(user_id):
        progress = CourseRepository.get_progress(user_id)
        return [{"course_name": p['playlist_id'], "progress": p['progress']} for p in progress]

    @staticmethod
    def save_progress(user_id, data):
        playlist_id = data.get('playlist_id')
        video_id = data.get('video_id')
        completed = data.get('completed', False)
        
        overall_progress = data.get('overall_progress')
        completed_videos = data.get('completed_videos')
        total_videos = data.get('total_videos')

        if video_id:
            CourseRepository.save_video_progress(user_id, playlist_id, video_id, completed)

        if overall_progress is not None:
            CourseRepository.save_playlist_progress(
                user_id, playlist_id, overall_progress, completed_videos, total_videos
            )
        return {"success": True}

    @staticmethod
    def get_playlist_progress(user_id, playlist_id):
        videos_progress = CourseRepository.get_video_progress(user_id, playlist_id)
        videos_dict = {v['video_id']: {'completed': v['completed']} for v in videos_progress} if videos_progress else {}
        
        stats = CourseRepository.get_playlist_stats(user_id, playlist_id)

        return {
            "success": True,
            "user_id": user_id,
            "playlist_id": playlist_id,
            "completed_videos": stats['completed_videos'] if stats else 0,
            "total_videos": stats['total_videos'] if stats else 0,
            "progress_percentage": stats['overall_progress'] if stats else 0,
            "videos": videos_dict
        }

class AIChatService:
    @staticmethod
    def get_reply(user_message):
        # Option 1: OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful e-learning assistant for SkillUp platform."},
                        {"role": "user", "content": user_message}
                    ]
                )
                return response.choices[0].message.content
            except Exception:
                pass

        # Option 2: Local Ollama
        ollama_url = "http://localhost:11434/api/generate"
        ollama_payload = {
            "model": "llama3.2",
            "prompt": f"Help student with SkillUp platform. Msg: {user_message}",
            "stream": False
        }

        try:
            response = requests.post(ollama_url, json=ollama_payload, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', '')
        except requests.exceptions.ConnectionError:
            return 'عذراً، نظام الدردشة يتطلب تشغيل Ollama محلياً.'
        
        return 'عذراً، حدث خطأ في نظام الدردشة.'
