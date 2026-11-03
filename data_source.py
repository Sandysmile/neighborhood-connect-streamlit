"""Read public Houston data and normalize fields shared by the directory UI."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import requests

API = 'https://houstontxsandbox.ogopendata.com/api/3/action/datastore_search'
RESOURCE = '6ee89d61-bd53-48a1-b611-3208d1844e16'
SOURCE = 'https://houstontxsandbox.ogopendata.com/dataset/superneighborhooddirectory'

def clean(value):
    return re.sub(r'\s+', ' ', str(value or '').replace(';#', ' ')).strip()

def normalize(row):
    fields = {'number':'SN #', 'name':'SN Name', 'status':'Active',
              'liaison':'Liaison', 'day':'Meeting Day', 'time':'Meeting Time',
              'frequency':'Meeting Frequency', 'recognized':'Recognized Date',
              'email':'SN Email', 'website':'SN Website', 'address':'SN Address',
              'venue':'Meeting Location', 'format':'Meeting Type',
              'contact':'Name', 'position':'SN Position'}
    result = {key:clean(row.get(source)) for key, source in fields.items()}
    result['districts'] = sorted(set(re.findall(r'\b[A-K]\b', clean(row.get('Council District')))))
    return result

def website_url(value):
    value = clean(value)
    if not value:
        return None
    if not re.match(r'^https?://', value, re.I):
        if '://' in value or re.match(r'^[a-z]+:', value, re.I):
            return None
        value = 'https://' + value
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or '.' not in parsed.hostname:
        return None
    if parsed.username or parsed.password or any(c.isspace() for c in value):
        return None
    return value

def email_url(value):
    addresses = re.findall(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', clean(value))
    return 'mailto:' + ','.join(dict.fromkeys(addresses)) if addresses else None

def load_records():
    try:
        rows = []
        offset = 0
        while True:
            response = requests.get(API, params={'resource_id':RESOURCE, 'limit':1000, 'offset':offset}, timeout=12)
            response.raise_for_status()
            payload = response.json()
            if not payload.get('success'):
                raise ValueError('Portal did not return successful data')
            result = payload['result']
            batch = result['records']
            rows.extend(batch)
            offset += len(batch)
            if offset >= int(result.get('total', offset)) or not batch:
                break
        if not rows or not all('SN Name' in row for row in rows):
            raise ValueError('Unexpected directory columns')
        return [normalize(row) for row in rows], False
    except (requests.RequestException, ValueError, KeyError, TypeError):
        rows = json.loads(Path(__file__).with_name('data_snapshot.json').read_text())
        return [normalize(row) for row in rows], True

def filter_records(rows, query='', district='All districts', status='All statuses'):
    query = query.strip().casefold()
    return sorted([
        row for row in rows
        if (not query or query in row['name'].casefold() or query in row['number'])
        and (district == 'All districts' or district in row['districts'])
        and (status == 'All statuses' or status == row['status'])
    ], key=lambda row:row['name'].casefold())
