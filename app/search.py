import pandas as pd
from config.settings import get_settings
from services.synthesizer import Synthesizer
import psycopg2

settings = get_settings()


def semantic_search(query_text: str, limit: int = 15) -> list[tuple]:
    with psycopg2.connect(settings.database.service_url) as conn:
        with conn.cursor() as cursor:
            search_query = """
                SELECT embedding_uuid, chunk
                FROM news_embedding_oai_small
                ORDER BY embedding <=> (
                    SELECT ai.openai_embed('text-embedding-3-small', %s)
                )
                LIMIT %s;
            """
            try:
                cursor.execute(search_query, (query_text, limit))
                result = cursor.fetchall()
                return pd.DataFrame(result, columns=["id", "chunk"])
            except psycopg2.Error as e:
                raise RuntimeError(
                    f"Failed to execute similarity search: {str(e)}"
                ) from e


question = "Is there any news about London?"
result = semantic_search(question)


answer = Synthesizer.generate_response(question, result)
print(answer.answer)
