import os
import sys
import json
import redis
import argparse
from mongoengine import connect
from models import Author, Quote

# UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def get_redis():
    redis_url = os.environ.get('REDIS_URL')
    if not redis_url:
        return None
    return redis.from_url(redis_url, decode_responses=True)

def ensure_connection():
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        print('Please set MONGO_URI environment variable (mongodb+srv://...).', file=sys.stderr)
        sys.exit(1)
    connect(host=mongo_uri)

def serialize_quotes(qs):
    out = []
    for q in qs:
        out.append({
            'quote': q.quote,
            'author': q.author.fullname if q.author else None,
            'tags': q.tags
        })
    return json.dumps(out, ensure_ascii=False, indent=2)

def find_by_name(name_value):
    author = Author.objects(fullname__iexact=name_value).first()
    if author:
        return Quote.objects(author=author)
    authors = Author.objects(fullname__istartswith=name_value)
    return Quote.objects(author__in=authors)

def find_by_tag(tag_value):
    qs = Quote.objects(tags__icontains=tag_value)
    if qs.count() > 0:
        return qs
    raw = {'tags': {'$elemMatch': {'$regex': f'^{tag_value}', '$options': 'i'}}}
    return Quote.objects(__raw__=raw)

def find_by_tags_list(tags_list):
    return Quote.objects(tags__in=tags_list)

def main_loop(redis_client=None):
    print('Interactive search CLI. Commands: name:<value>, tag:<value>, tags:tag1,tag2, exit')
    while True:
        try:
            cmd = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nexit')
            break
        if not cmd:
            continue
        if cmd.lower() == 'exit':
            break
        if ':' not in cmd:
            print('Wrong format. Use command:value')
            continue
        command, value = cmd.split(':', 1)
        command = command.strip().lower()
        value = value.strip()
        cache_key = f'{command}:{value}'

        if redis_client and command in ('name', 'tag'):
            cached = redis_client.get(cache_key)
            if cached:
                print('(from cache)')
                print(cached)
                continue

        if command == 'name':
            qs = find_by_name(value)
            out = serialize_quotes(qs)
            print(out)
            if redis_client:
                redis_client.set(cache_key, out)
        elif command == 'tag':
            qs = find_by_tag(value)
            out = serialize_quotes(qs)
            print(out)
            if redis_client:
                redis_client.set(cache_key, out)
        elif command == 'tags':
            tags_list = [t.strip() for t in value.split(',') if t.strip()]
            qs = find_by_tags_list(tags_list)
            out = serialize_quotes(qs)
            print(out)
        else:
            print('Unknown command. Supported: name, tag, tags, exit')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-redis', action='store_true', help='Disable Redis caching')
    args = parser.parse_args()

    ensure_connection()
    r = None
    if not args.no_redis:
        r = get_redis()
        if r is None:
            print('REDIS_URL not set — running without Redis cache.')

    main_loop(redis_client=r)
