import json
import argparse
import os
import sys
from mongoengine import connect
from models import Author, Quote

def ensure_connection():
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print('Please set MONGO_URI environment variable (mongodb+srv://...).', file=sys.stderr)
        sys.exit(1)
    connect(host=mongo_uri)

def load_authors(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    inserted = 0
    for a in data:
        obj, created = Author.objects(fullname=a['fullname']).modify(
            upsert=True, new=True,
            fullname=a['fullname'],
            born_date=a.get('born_date'),
            born_location=a.get('born_location'),
            description=a.get('description')
        )
        inserted += 1
    print(f'Processed {inserted} authors')

def load_quotes(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    inserted = 0
    for q in data:
        author_name = q.get('author')
        if not author_name:
            continue
        author = Author.objects(fullname__iexact=author_name).first()
        if not author:
            print(f'Author "{author_name}" not found in DB — skipping quote.', file=sys.stderr)
            continue
        Quote.objects(quote=q['quote']).modify(
            upsert=True, new=True,
            set__author=author,
            set__tags=q.get('tags', []),
            set__quote=q['quote']
        )
        inserted += 1
    print(f'Processed {inserted} quotes')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--authors', required=True)
    parser.add_argument('--quotes', required=True)
    args = parser.parse_args()

    ensure_connection()
    load_authors(args.authors)
    load_quotes(args.quotes)
