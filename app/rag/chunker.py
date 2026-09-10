import os
import re
from dotenv import load_dotenv
from google import genai

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return sentences

def sentence_chunker(text, chunk_size=100, overlap=1):
    sentences = split_sentences(text)

    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence.split())
        if current_size + sentence_size <= chunk_size:
            current_chunk.append(sentence)
            current_size += sentence_size
        else:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            overlap_sentences = current_chunk[-overlap:]
            current_chunk = overlap_sentences + [sentence]
            current_size = sum(len(s.split()) for s in current_chunk)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks