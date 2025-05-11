import sqlite3


def create_tables():
    db = sqlite3.connect("shorts.db")
    cursor = db.cursor()

    create_uploads_table = """
    CREATE TABLE IF NOT EXISTS uploads (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id VARCHAR(30),
        top_comment_id VARCHAR(30)
    );
    """

    create_admin_table = """
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        submission_id VARCHAR(30)
    );
    """

    cursor.execute(create_uploads_table)
    cursor.execute(create_admin_table)

    db.commit()

    cursor.close()
    db.close()


def check_if_video_exists(submission_id: str, top_comment_id: str) -> bool:
    db = sqlite3.connect("shorts.db")
    cursor = db.cursor()

    videos_query = """
        SELECT * FROM uploads
        WHERE submission_id = ?
        AND top_comment_id = ?;
        """

    cursor.execute(videos_query, (submission_id, top_comment_id))
    rows = cursor.fetchall()

    if len(rows) > 0:
        video_exists = True
        print("Video found in DB!")

    else:
        video_exists = False
        print("Video not in DB!")

    db.commit()
    cursor.close()
    db.close()

    return video_exists


def write_to_db(submission_id: str, top_comment_id: str) -> None:
    db = sqlite3.connect("shorts.db")
    cursor = db.cursor()

    write_to_videos = """
    INSERT INTO uploads (submission_id, top_comment_id)
    VALUES (?, ?);
    """

    cursor.execute(write_to_videos, (submission_id, top_comment_id))
    db.commit()

    print("Updated DB")

    cursor.close()
    db.close()


def check_for_admin_posts(submission_id: str) -> bool:
    db = sqlite3.connect("shorts.db")
    cursor = db.cursor()

    videos_query = """
        SELECT * FROM admin
        WHERE submission_id = ?;
        """

    cursor.execute(videos_query, (submission_id,))
    rows = cursor.fetchall()

    if len(rows) > 0:
        admin_post = True
        print("This Submission was written by an Admin")

    else:
        admin_post = False
        # print("Video not in DB!")

    db.commit()
    cursor.close()
    db.close()

    return admin_post
