SELECT ai.create_vectorizer(
    'public.news'::regclass, 
    destination => 'news_embedding_oai_small'
  , embedding=>ai.embedding_openai('text-embedding-3-small', 1536, api_key_name=>'OPENAI_API_KEY')
  , chunking=>ai.chunking_recursive_character_text_splitter('article')
  , formatting=>ai.formatting_python_template('Article summary: $summary article chunk: $chunk')
);
