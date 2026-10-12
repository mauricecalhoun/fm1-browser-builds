#!/usr/bin/env python3
"""Serve FM-1 Lab and proxy only the public Firmware Hub catalog.
No external request accepts a user-controlled URL.
"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse, parse_qs
import re
import json
import os

CATALOG_URL = 'https://fm1.designburgapps.com/catalog.json'
# GitHub repo containing browser-build releases, e.g. yourname/fm1-browser-builds.
BUILD_REPO = os.environ.get('FM1_BROWSER_BUILD_REPO', 'mauricecalhoun/fm1-browser-builds').strip()
def github_repo(firmware_id):
    # Only repos advertised by the live Hub; no arbitrary URL proxy.
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', firmware_id):
        raise ValueError('Invalid firmware ID')
    request = Request(CATALOG_URL, headers={'User-Agent':'FM1-Firmware-Lab/1.3'})
    with urlopen(request, timeout=10) as response:
        catalog = json.loads(response.read(1024*1024))
    item = next((f for f in catalog.get('firmwares',[]) if f.get('id')==firmware_id),None)
    if not item: raise ValueError('Firmware not in live catalog')
    repo = item.get('repo','')
    if not isinstance(repo,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):
        raise ValueError('No valid GitHub repository for firmware')
    return repo

class Handler(SimpleHTTPRequestHandler):
    def json_response(self, obj, status=200):
        raw=json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def github_release(self, firmware_id):
        upstream=github_repo(firmware_id)
        repo=BUILD_REPO if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', BUILD_REPO) else upstream
        request=Request(f'https://api.github.com/repos/{repo}/releases?per_page=30',headers={'User-Agent':'FM1-Firmware-Lab/1.3','Accept':'application/vnd.github+json'})
        with urlopen(request,timeout=12) as response:
            releases=json.loads(response.read(1024*1024))
        for release in releases:
            if release.get('draft') or release.get('prerelease'):continue
            assets=release.get('assets',[])
            packages=[a for a in assets if a.get('name','').lower()==firmware_id.lower()+'.fm1pkg']
            for pkg in packages:
                checksum=next((a for a in assets if a.get('name')==pkg['name']+'.sha256'),None)
                if checksum:
                    return {'available':True,'repo':repo,'version':release.get('tag_name',''), 'published_at':release.get('published_at'), 'release_url':release.get('html_url'), 'recipe':('upstream-felucca' if firmware_id=='felucca' else 'bundled-sloop-port' if firmware_id=='sloop' else 'unknown'), 'upstream':upstream, 'package_asset_id':pkg['id'],'checksum_asset_id':checksum['id'],'size':pkg.get('size',0)}
        return {'available':False,'repo':repo,'reason':'Browser port needed: no compatible package published for this firmware. Hardware .fwsc images cannot run in Safari.'}
    def github_asset(self,firmware_id,asset_id,limit):
        info=self.github_release(firmware_id)
        repo=info['repo']
        if not info.get('available') or asset_id not in (info['package_asset_id'],info['checksum_asset_id']):
            raise ValueError('Asset not in approved browser release')
        req=Request(f'https://api.github.com/repos/{repo}/releases/assets/{asset_id}',headers={'User-Agent':'FM1-Firmware-Lab/1.3','Accept':'application/octet-stream','X-GitHub-Api-Version':'2022-11-28'})
        with urlopen(req,timeout=30) as response:
            raw=response.read(limit+1)
            if len(raw)>limit:raise ValueError('Asset exceeds limit')
            content_type=response.headers.get('Content-Type','')
        if content_type.startswith('application/json'):
            raise ValueError('GitHub returned asset metadata instead of file bytes')
        self.send_response(200)
        self.send_header('Content-Type','application/octet-stream')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path=urlparse(self.path).path
        match=re.fullmatch(r'/api/repository/([A-Za-z0-9_-]{1,64})',path)
        asset=re.fullmatch(r'/api/repository/([A-Za-z0-9_-]{1,64})/asset/([0-9]{1,20})',path)
        if match or asset:
            try:
                if match:self.json_response(self.github_release(match.group(1)))
                else:self.github_asset(asset.group(1),int(asset.group(2)),32*1024*1024)
            except (URLError,HTTPError,TimeoutError,ValueError,OSError,KeyError) as exc:
                self.json_response({'error':str(exc)},502)
            return
        if path != '/api/catalog':
            return super().do_GET()
        try:
            request = Request(CATALOG_URL, headers={'User-Agent':'FM1-Firmware-Lab/0.8'})
            with urlopen(request, timeout=10) as response:
                raw=response.read(1024*1024+1)
            if len(raw)>1024*1024: raise ValueError('Catalog too large')
            data=json.loads(raw)
            if not isinstance(data,dict) or not isinstance(data.get('firmwares'),list):
                raise ValueError('Unexpected catalog format')
            self.send_response(200)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            self.wfile.write(raw)
        except (URLError, TimeoutError, ValueError, OSError) as error:
            self.send_error(502, 'Firmware Hub catalog unavailable')
if __name__=='__main__':
    print('FM-1 Firmware Lab: http://localhost:8000')
    ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
