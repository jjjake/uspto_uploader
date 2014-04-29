#!/usr/bin/env python
import pathlib
import sys

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
def get_metadata(item, item_dir):
    pdfs = list(item_dir.glob('*pdf'))
    html = ('United States Patent and Trademark Office documents.<br /><br />Click the '
            'links below to access the documents in this item:<br />')
    for pdf in pdfs:
        url = '//archive.org/download/{i}/{f}'.format(i=item.identifier, f=pdf.name)
        html += '<a href="{u}">{f}</a><br />'.format(u=url, f=pdf.name)
    _title = item.identifier.split('gov.')[-1].replace('.', ' ')
    title = _title.title().replace('Uspto', 'USPTO')
    md = dict(
        collection='uspto',
        mediatype='texts',
        subject=['U.S. Patents', 'U.S. Trademarks'],
        language='eng',
        description=html,
        title=title,
    )
    return md


# main()
# ________________________________________________________________________________________
if __name__ == '__main__':
    for i in item_generator():
        identifier = '-'.join(str(i).split('/')[3:])

        config = {'logging': {'level': 'INFO'}}
        item = get_item(identifier, config=config)

        print('{0}:'.format(item.identifier))

        # Add trailing slash to upload contents of dir, not dir itself.
        item_dir = '{d}/'.format(d=str(i))
        md = get_metadata(item, i)
        resps = item.upload(item_dir, metadata=md, verbose=True, checksum=True)
        sys.exit()
