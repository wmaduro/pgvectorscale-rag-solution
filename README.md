# Quickstart: Automated Vector Embeddings with PostgreSQL

This guide demonstrates how to use Timescale's new vectorizer feature to automatically generate and maintain vector embeddings in PostgreSQL. Instead of managing embeddings in your application code, you can now handle them directly in your database using a SQL-level interface.

## Further documenation

- [Vector Databases Are the Wrong Abstraction](https://www.timescale.com/blog/vector-databases-are-the-wrong-abstraction/)
- [Vectorizer Quick Start](https://github.com/timescale/pgai/blob/main/docs/vectorizer-quick-start.md)
- [Automate AI embedding with pgai Vectorizer](https://github.com/timescale/pgai/blob/main/docs/vectorizer.md)
- [Vectorizer Worker](https://github.com/timescale/pgai/blob/main/docs/vectorizer-worker.md)
  
## Prerequisites

- Docker Desktop
- PostgreSQL GUI client (e.g., TablePlus, pgAdmin)
- OpenAI API key
- Python 3.7+

## Setup

1. Clone this repository and create your TWO `.env` files:
   
```bash
cp app/example.env app/.env
cp docker/example.env app/.env
```

1. Add your OpenAI API key to the `.env` file:
   
```
OPENAI_API_KEY=your_key_here
```

1. Start the Docker containers:
   
```bash
docker compose up -d
```

This will start two services:

- A PostgreSQL database using Timescale's image
- A vectorizer worker that automatically maintains your embeddings

## Database Setup

The initialization happens automatically through three SQL files in `docker/init-db/`:

1. Extensions setup (`01-init.sql`):

```sql
CREATE EXTENSION IF NOT EXISTS ai CASCADE;
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;
```

1. Base table creation (`02-init.sql`):

```sql
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    article TEXT,
    highlights TEXT,
    summary TEXT
);
```

1. Vectorizer configuration (`03-init.sql`):

```sql
SELECT ai.create_vectorizer(
    'public.news'::regclass,
    destination => 'news_embedding_oai_small',
    embedding => ai.embedding_openai('text-embedding-3-small', 1536, api_key_name=>'OPENAI_API_KEY'),
    chunking => ai.chunking_recursive_character_text_splitter('article'),
    formatting => ai.formatting_python_template('Article summary: $summary article chunk: $chunk')
);
```

## Loading Sample Data

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

1. Run the sample data loader:

```bash
python app/upsert.py
```

This will load sample articles from the CNN/Daily Mail dataset.

## Checking the Results

Connect to the database using your PostgreSQL GUI client:

- Host: localhost
- Port: 5432
- User: postgres
- Password: password
- Database: postgres

You should see:

- `news` table with your raw articles
- `news_embedding_oai_small` table containing the vector embeddings
- A view that joins the base table with embeddings

Run the following command to check the que:

```sql
SELECT * FROM ai.vectorizer_status;
```

## Automatic Embedding Updates

The vectorizer worker runs every 5 minutes to keep embeddings in sync with your source data. To manually trigger an update, stop the container and run:

```bash
docker compose up -d vectorizer-worker
```

## Performing Similarity Search

Try out semantic search using the provided script:

```bash
python app/search.py
```

This will perform a similarity search using OpenAI's embeddings and return relevant article chunks based on your query.

## How It Works

1. The `ai.create_vectorizer()` function sets up automatic embedding generation for your table
2. When you insert/update data in the `news` table, the vectorizer worker detects changes
3. The worker automatically generates embeddings using OpenAI's API
4. Embeddings are stored in a separate table that's automatically kept in sync
5. You can perform similarity searches using the `<=>` operator with the stored embeddings

This approach eliminates the need to manage embeddings in your application code, making it easier to build semantic search features into your PostgreSQL applications.

## Next Steps

- Explore different chunking strategies in the vectorizer configuration
- Try different embedding models
- Implement hybrid search combining traditional and vector search

For more details on available options and advanced features, see the [Vectorizer API reference](https://github.com/timescale/pgai/blob/main/docs/vectorizer.md). 

## More SQL Examples

Here are some additional SQL commands to help you manage your vectorizers:

### Creating Additional Vectorizers

Create a vectorizer using OpenAI's larger embedding model:

```sql
-- Create a vectorizer with text-embedding-3-large
SELECT ai.create_vectorizer(
    'public.news'::regclass, 
    destination => 'news_embedding_oai_large',
    embedding => ai.embedding_openai('text-embedding-3-large', 3072, api_key_name=>'OPENAI_API_KEY'),
    chunking => ai.chunking_recursive_character_text_splitter('article'),
    formatting => ai.formatting_python_template('Article summary: $summary article chunk: $chunk')
);
```

### Monitoring Vectorizers

Check the status and configuration of your vectorizers:

```sql
-- List all configured vectorizers
SELECT * FROM ai.vectorizer;

-- Check processing status and queue
SELECT * FROM ai.vectorizer_status;
```

### Cleanup Operations

Remove a vectorizer and its associated objects:

```sql
DO $$
DECLARE
    target_name TEXT := 'blogs_embedding';
BEGIN
    -- Delete the vectorizer entry
    DELETE FROM ai.vectorizer
    WHERE target_schema = 'public' 
    AND target_table = target_name || '_store';
    
    -- Drop the view if it exists
    EXECUTE format('DROP VIEW IF EXISTS public.%I', target_name);

    -- Drop the table if it exists
    EXECUTE format('DROP TABLE IF EXISTS public.%I', target_name || '_store');
END $$;
```

These commands help you manage the full lifecycle of your vectorizers, from creation to monitoring and cleanup.
