import psycopg2
from googletrans import Translator

# PostgreSQL connection setup
conn = psycopg2.connect(
    host="localhost",      # Replace with your PostgreSQL host (default: localhost)
    database="postgres",    # Replace with your PostgreSQL database name
    user="postgres",      # Replace with your PostgreSQL username
    password="qwerty"  # Replace with your PostgreSQL password
)
cur = conn.cursor()

# Initialize the Google Translator
translator = Translator()

# Function to translate text and comments and update the database
def translate_and_update():
    try:
        # Select rows from 'dialogue_base' where either 'text' or 'comments' is not NULL
        cur.execute("SELECT id, text, comments FROM public.dialogue_base WHERE text IS NOT NULL OR comments IS NOT NULL")
        rows = cur.fetchall()

        # Check if rows are returned
        if rows is None or len(rows) == 0:
            print("No rows found to update.")
            return  # Exit the function if no rows are returned

        for row in rows:
            backend_id = row[0]
            original_text = row[1]
            original_comments = row[2]
            print(f"Processing ID: {backend_id}")

            try:
                # Translate 'text' column if it is not NULL
                if original_text:
                    translated_text = translator.translate(original_text, dest='uk').text
                    cur.execute("UPDATE public.dialogue_base SET text = %s WHERE id = %s", (translated_text, backend_id))

                # Translate 'comments' column if it is not NULL
                if original_comments:
                    translated_comments = translator.translate(original_comments, dest='uk').text
                    cur.execute("UPDATE public.dialogue_base SET comments = %s WHERE id = %s", (translated_comments, backend_id))

            except Exception as e:
                # If an error occurs, print the id, text, and comments and prompt for manual input
                print(f"Error translating ID {backend_id}: {e}")
                print(f"Text: {original_text}")
                print(f"Comments: {original_comments}")

                # Prompt user for manual translation input
                manual_translation_text = input("Enter manual translation for 'text' (leave empty if no translation needed): ")
                if manual_translation_text:
                    cur.execute("UPDATE public.dialogue_base SET text = %s WHERE id = %s", (manual_translation_text, backend_id))

                manual_translation_comments = input("Enter manual translation for 'comments' (leave empty if no translation needed): ")
                if manual_translation_comments:
                    cur.execute("UPDATE public.dialogue_base SET comments = %s WHERE id = %s", (manual_translation_comments, backend_id))

        # Commit changes to the database
        conn.commit()
        print("Translations updated successfully!")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

# Run the translation function
if __name__ == "__main__":
    translate_and_update()
