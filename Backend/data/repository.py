from .db import execute_query

class UserRepository:
    @staticmethod
    def get_by_identity(identity):
        return execute_query(
            "SELECT user_id, name, email, password, role, profile_image, age, year, major, college FROM Users WHERE LOWER(name)=LOWER(%s) OR LOWER(email)=LOWER(%s)",
            (identity, identity),
            fetch_one=True
        )

    @staticmethod
    def get_by_id(user_id):
        return execute_query(
            "SELECT user_id, name, email, role FROM Users WHERE user_id=%s",
            (user_id,),
            fetch_one=True
        )

    @staticmethod
    def get_by_email(email):
        return execute_query("SELECT * FROM Users WHERE LOWER(email)=LOWER(%s)", (email,), fetch_one=True)

    @staticmethod
    def create(name, email, hashed_password, role):
        return execute_query(
            "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )

    @staticmethod
    def update_password(user_id, hashed_password):
        return execute_query("UPDATE Users SET password=%s WHERE user_id=%s", (hashed_password, user_id))

    @staticmethod
    def update_profile(user_id, name, profile_image, age, year, major, college):
        # Note: In the original app, it used email to update. user_id is safer but let's stick to email if needed, 
        # or better, refactor to ID. Let's use email to maintain compatibility with existing frontend for now.
        return execute_query(
            "UPDATE Users SET name=%s, profile_image=%s, age=%s, year=%s, major=%s, college=%s WHERE user_id=%s",
            (name, profile_image, age, year, major, college, user_id)
        )
    
    @staticmethod
    def update_profile_by_email(email, name, profile_image, age, year, major, college):
        return execute_query(
            "UPDATE Users SET name=%s, profile_image=%s, age=%s, year=%s, major=%s, college=%s WHERE email=%s",
            (name, profile_image, age, year, major, college, email)
        )

class CourseRepository:
    @staticmethod
    def get_all():
        return execute_query("SELECT * FROM Courses", fetch_all=True)

    @staticmethod
    def get_progress(user_id):
        return execute_query(
            "SELECT playlist_id, overall_progress as progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s",
            (user_id,),
            fetch_all=True
        )

    @staticmethod
    def save_video_progress(user_id, playlist_id, video_id, completed):
        return execute_query(
            "INSERT INTO VideoProgress (user_id, playlist_id, video_id, completed) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (user_id, playlist_id, video_id) DO UPDATE SET completed=EXCLUDED.completed, updated_at=CURRENT_TIMESTAMP",
            (user_id, playlist_id, video_id, completed)
        )

    @staticmethod
    def save_playlist_progress(user_id, playlist_id, overall_progress, completed_videos, total_videos):
        return execute_query(
            "INSERT INTO PlaylistProgress (user_id, playlist_id, overall_progress, completed_videos, total_videos) VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT (user_id, playlist_id) DO UPDATE SET overall_progress=EXCLUDED.overall_progress, "
            "completed_videos=EXCLUDED.completed_videos, total_videos=EXCLUDED.total_videos, last_updated=CURRENT_TIMESTAMP",
            (user_id, playlist_id, overall_progress, completed_videos, total_videos)
        )

    @staticmethod
    def get_video_progress(user_id, playlist_id):
        return execute_query(
            "SELECT video_id, completed FROM VideoProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_all=True
        )

    @staticmethod
    def get_playlist_stats(user_id, playlist_id):
        return execute_query(
            "SELECT overall_progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_one=True
        )
