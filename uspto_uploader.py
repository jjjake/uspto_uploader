#!/usr/bin/env python
import pathlib
import sys
import csv

from internetarchive import get_item, log


__author__ = 'Jake Johnson'
__license__ = 'AGPL 3'
__copyright__ = 'Copyright 2014 Internet Archive'


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
    if csv_md['title']:
        md['description'] = [csv_md['title'], md['description']]
    del csv_md['title']
    md.update(csv_md)
    return dict((k, v) for (k, v) in md.items() if v)


# main()
# ________________________________________________________________________________________
if __name__ == '__main__':
    for i in item_generator():
        identifier = str(i).split('/')[-1]

        config = {'logging': {'level': 'INFO'}}
        item = get_item(identifier, config=config)

        print('{0}:'.format(item.identifier))

        # Add trailing slash to upload contents of dir, not dir itself.
        item_dir = '{d}/'.format(d=str(i))
        md = get_metadata(item, i)
        h = {'x-archive-queue-derive': 0}
        #resps = item.upload(item_dir, metadata=md, headers=h, verbose=True, checksum=True)

        # Update metadata.
        #resp = item.modify_metadata(md)
