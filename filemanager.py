def remove_file(file_id, uploads_folder):
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host='your_host',
            user='your_user',
            password='your_password',
            database='your_database'
        )

        cursor = connection.cursor(dictionary=True)

        # Step 1: Retrieve the file path and ensure the file exists in the DB
        cursor.execute("SELECT path FROM files WHERE id = %s", (file_id,))
        file_record = cursor.fetchone()

        if not file_record:
            print("File not found in the database.")
            return False

        file_path = file_record['path']
        absolute_path = os.path.join(uploads_folder, file_path)

        # Step 2: Delete the file from the filesystem
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            print(f"File {absolute_path} deleted successfully.")
        else:
            print(f"File {absolute_path} not found on the filesystem.")

        # Step 3: Delete the record from the database
        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        connection.commit()
        print("File record deleted from the database.")

        return True

    except Error as e:
        print(f"Error: {e}")
        return False

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()