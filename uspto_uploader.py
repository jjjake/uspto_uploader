#!/usr/bin/env python
import pathlib
import sys
import csv
import time

import futures
from internetarchive import get_item, get_tasks


__author__ = 'Jake Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2014 Internet Archive'


# Global settings.
MAX_WORKERS = 10
MAX_GREEN_ROWS = 300
SLEEP_TIME = 60


# item_generator()
# ________________________________________________________________________________________
def item_generator():
    p = pathlib.Path('/Volumes/patent')
    prev_dir = None
    for f in p.glob('**/*pdf'):
        if str(f).startswith('/Volumes/patent/.'):
            continue
        if prev_dir != f.parent:
            prev_dir = f.parent
            yield f.parent
        else:
            prev_dir = f.parent


# get_metadata()
# ________________________________________________________________________________________
def get_csv_metadata(identifier):
    f = open('/Volumes/patent/patentapplications.csv') 
    for md in csv.DictReader(f):
        if md.get('folder') == identifier:
            del md['source']
            del md['folder']
            # Empty date values are represented as "0000-00-00", do not
            # include these fields!
            return dict((k, v) for (k, v) in md.items() if (v) and (v != '0000-00-00'))


# get_metadata()
# ________________________________________________________________________________________
def get_metadata(item, item_dir):
    pdfs = list(item_dir.glob('*pdf'))
    html = ('<b>Click the links below to access the documents in this item:</b>'
            '<br /><br />')
    for pdf in pdfs:
        url = '//archive.org/download/{i}/{f}'.format(i=item.identifier, f=pdf.name)
        html += ('{f} <a href="//archive.org/download/{id}/{f}_text.pdf">pdf</a>'
                 ' <a href="//archive.org/stream/{id}/{f}">stream</a>'
                 '<br />'.format(f=pdf.stem, id=item.identifier))
    _title = item.identifier.split('gov.')[-1].replace('.', ' ')
    title = _title.title().replace('Uspto', 'USPTO')
    md = dict(
        collection='uspto',
        mediatype='texts',
        contributor='Think Computer Foundation',
        creator='United States Patent and Trademark Office',
        subject=['U.S. Patents'],
        language='eng',
        description=html,
        title=title,
    )
    csv_md = get_csv_metadata(item.identifier)
    if csv_md.get('title'):
        md['description'] = [csv_md['title'], md['description']]
    del csv_md['title']
    md.update(csv_md)
    return dict((k, v) for (k, v) in md.items() if v)


# upload()
# ________________________________________________________________________________________
def upload(path):
    # Throttle task submission if number of green rows exceeds 
    # MAX_GREEN_ROWS.
    tasks = [t for t in get_tasks(task_type='green') if 'gov.uspto' in t.identifier]
    while len(tasks) >= MAX_GREEN_ROWS:
        print('{0} green rows, pausing for {1} seconds.'.format(len(tasks), SLEEP_TIME))
        time.sleep(SLEEP_TIME)

    identifier = str(path).split('/')[-1]
    config = {'logging': {'level': 'INFO'}}
    item = get_item(identifier, config=config)

    # Add trailing slash to upload contents of dir, not dir itself.
    item_dir = '{d}/'.format(d=str(path))
    md = get_metadata(item, path)
    h = {'x-archive-queue-derive': 0}
    resp = item.upload(item_dir, metadata=md, headers=h, verbose=True, checksum=True)

    # Update metadata.
    #resp = item.modify_metadata(md)

    return resp


# main()
# ________________________________________________________________________________________
if __name__ == '__main__':
    with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_path = {
            executor.submit(upload, path): path for path in item_generator()
        }
        for future in futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                resp = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (path, exc))
