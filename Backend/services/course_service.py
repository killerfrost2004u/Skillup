import os
import requests
from datetime import datetime
from abc import ABC, abstractmethod

# ============================================
# 5. OBSERVER PATTERN (Event System)
# ============================================
class ProgressObserver(ABC):
    @abstractmethod
    def update(self, user_id, playlist_id, percent):
        pass

class CompletionLogger(ProgressObserver):
    def update(self, user_id, playlist_id, percent):
        if percent >= 100:
            print(f"🎉 User {user_id} COMPLETED {playlist_id}!")

class CourseService:
    def __init__(self, course_repo):
        self.course_repo = course_repo
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def _notify_observers(self, user_id, playlist_id, percent):
        for observer in self.observers:
            observer.update(user_id, playlist_id, percent)

    def get_all_courses(self):
        return self.course_repo.get_all()

    def get_user_progress(self, user_id):
        progress = self.course_repo.get_progress(user_id)
        return [{"course_name": p['playlist_id'], "progress": p['progress']} for p in progress]

    def save_progress(self, user_id, data):
        playlist_id = data.get('playlist_id')
        video_id = data.get('video_id')
        completed = data.get('completed', False)
        
        overall_progress = data.get('overall_progress')
        completed_videos = data.get('completed_videos')
        total_videos = data.get('total_videos')

        if video_id:
            self.course_repo.save_video_progress(user_id, playlist_id, video_id, completed)

        if overall_progress is not None:
            self.course_repo.save_playlist_progress(
                user_id, playlist_id, overall_progress, completed_videos, total_videos
            )
            self._notify_observers(user_id, playlist_id, overall_progress)
            
        return {"success": True}

    def get_playlist_progress(self, user_id, playlist_id):
        videos_progress = self.course_repo.get_video_progress(user_id, playlist_id)
        videos_dict = {v['video_id']: {'completed': v['completed']} for v in videos_progress} if videos_progress else {}
        
        stats = self.course_repo.get_playlist_stats(user_id, playlist_id)

        return {
            "success": True,
            "user_id": user_id,
            "playlist_id": playlist_id,
            "completed_videos": stats['completed_videos'] if stats else 0,
            "total_videos": stats['total_videos'] if stats else 0,
            "progress_percentage": stats['overall_progress'] if stats else 0,
            "videos": videos_dict
        }

# ============================================
# 6. STRATEGY PATTERN (AI Providers)
# ============================================
class ChatStrategy(ABC):
    @abstractmethod
    def generate_reply(self, message: str) -> str:
        pass

class OpenAIStrategy(ChatStrategy):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_reply(self, message: str) -> str:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful e-learning assistant for SkillUp platform."},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with OpenAI provider: {str(e)}"

class OllamaStrategy(ChatStrategy):
    def __init__(self, url: str = "http://localhost:11434/api/generate"):
        self.url = url

    def generate_reply(self, message: str) -> str:
        payload = {
            "model": "llama3.2",
            "prompt": f"Help student with SkillUp platform. Msg: {message}",
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get('response', '')
            return f"Ollama error: HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return 'عذراً، نظام الدردشة يتطلب تشغيل Ollama محلياً.'
        except Exception as e:
            return f"Error with Ollama provider: {str(e)}"

class AIChatService:
    def __init__(self, strategy: ChatStrategy):
        self.strategy = strategy

    def get_reply(self, user_message: str) -> str:
        if not self.strategy:
            return 'عذراً، نظام الدردشة غير متاح حالياً.'
        return self.strategy.generate_reply(user_message)
