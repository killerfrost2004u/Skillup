from .db import db_manager

# ============================================
# 3. REPOSITORY PATTERN (Formalized)
# ============================================
class UserRepository:
    def get_by_identity(self, identity):
        return db_manager.execute_query(
            "SELECT user_id, name, email, password, role, profile_image, age, year, major, college FROM Users WHERE LOWER(name)=LOWER(%s) OR LOWER(email)=LOWER(%s)",
            (identity, identity),
            fetch_one=True
        )

    def get_by_id(self, user_id):
        return db_manager.execute_query(
            "SELECT user_id, name, email, role FROM Users WHERE user_id=%s",
            (user_id,),
            fetch_one=True
        )

    def get_by_email(self, email):
        return db_manager.execute_query("SELECT * FROM Users WHERE LOWER(email)=LOWER(%s)", (email,), fetch_one=True)

    def create(self, name, email, hashed_password, role):
        return db_manager.execute_query(
            "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )

    def update_password(self, user_id, hashed_password):
        return db_manager.execute_query("UPDATE Users SET password=%s WHERE user_id=%s", (hashed_password, user_id))

    def update_profile_by_email(self, email, name, profile_image, age, year, major, college):
        return db_manager.execute_query(
            "UPDATE Users SET name=%s, profile_image=%s, age=%s, year=%s, major=%s, college=%s WHERE LOWER(email)=LOWER(%s)",
            (name, profile_image, age, year, major, college, email)
        )

class CourseRepository:
    def get_all(self):
        return db_manager.execute_query("SELECT * FROM Courses", fetch_all=True)

    def get_progress(self, user_id):
        return db_manager.execute_query(
            "SELECT playlist_id, overall_progress as progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s",
            (user_id,),
            fetch_all=True
        )

    def save_video_progress(self, user_id, playlist_id, video_id, completed):
        return db_manager.execute_query(
            "INSERT INTO VideoProgress (user_id, playlist_id, video_id, completed) VALUES (%s, %s, %s, %s) "
            "ON CONFLICT (user_id, playlist_id, video_id) DO UPDATE SET completed=EXCLUDED.completed, updated_at=CURRENT_TIMESTAMP",
            (user_id, playlist_id, video_id, completed)
        )

    def save_playlist_progress(self, user_id, playlist_id, overall_progress, completed_videos, total_videos):
        return db_manager.execute_query(
            "INSERT INTO PlaylistProgress (user_id, playlist_id, overall_progress, completed_videos, total_videos) VALUES (%s, %s, %s, %s, %s) "
            "ON CONFLICT (user_id, playlist_id) DO UPDATE SET overall_progress=EXCLUDED.overall_progress, "
            "completed_videos=EXCLUDED.completed_videos, total_videos=EXCLUDED.total_videos, last_updated=CURRENT_TIMESTAMP",
            (user_id, playlist_id, overall_progress, completed_videos, total_videos)
        )

    def get_video_progress(self, user_id, playlist_id):
        return db_manager.execute_query(
            "SELECT video_id, completed FROM VideoProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_all=True
        )

    def get_playlist_stats(self, user_id, playlist_id):
        return db_manager.execute_query(
            "SELECT overall_progress, completed_videos, total_videos FROM PlaylistProgress WHERE user_id=%s AND playlist_id=%s",
            (user_id, playlist_id),
            fetch_one=True
        )
