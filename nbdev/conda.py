# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/05a_conda.ipynb (unless otherwise specified).

__all__ = ['pypi_json', 'latest_pypi', 'write_pip_conda_meta', 'write_conda_meta']

# Cell
from .imports import *
from .export import *

import urllib.request,json,yaml
from copy import deepcopy
try: from packaging.version import parse
except ImportError: from pip._vendor.packaging.version import parse

_PYPI_URL = 'https://pypi.org/pypi/'

# Cell
def pypi_json(s):
    "Dictionary decoded JSON for PYPI path `s`"
    url = f'{_PYPI_URL}{s}/json'
    return json.loads(urllib.request.urlopen(url).read())

# Cell
def latest_pypi(name):
    "Latest version of `name` on pypi"
    return max(parse(r) for r,o in pypi_json(name)['releases'].items()
               if not parse(r).is_prerelease and not o[0]['yanked'])

# Cell
def _pip_conda_meta(name):
    ver = str(latest_pypi('sentencepiece'))
    pypi = pypi_json(f'{name}/{ver}')
    info = pypi['info']
    rel = [o for o in pypi['urls'] if o['packagetype']=='sdist'][0]
    reqs = ['pip', 'python', 'packaging']

    # Work around conda build bug - 'package' and 'source' must be first
    d1 = {
        'package': {'name': name, 'version': ver},
        'source': {'url':rel['url'], 'sha256':rel['digests']['sha256']}
    }
    d2 = {
        'build': {'number': '0', 'noarch': 'python',
                  'script': '{{ PYTHON }} -m pip install . -vv'},
        'test': {'imports': [name]},
        'requirements': {'host':reqs, 'run':reqs},
        'about': {'license': info['license'], 'home': info['project_url'], 'summary': info['summary']}
    }
    return d1,d2

# Cell
def _write_yaml(path, name, d1, d2):
    path = Path(path)
    p = path/name
    p.mkdir(exist_ok=True, parents=True)
    yaml.SafeDumper.ignore_aliases = lambda *args : True
    with (p/'meta.yaml').open('w') as f:
        yaml.safe_dump(d1, f)
        yaml.safe_dump(d2, f)

# Cell
def write_pip_conda_meta(name, path='conda'):
    "Writes a `meta.yaml` file for `name` to the `conda` directory of the current directory"
    _write_yaml(path, name, *_pip_conda_meta(name))

# Cell
def _get_conda_meta():
    cfg = Config()
    name,ver = cfg.get('lib_name'),cfg.get('version')
    url = cfg.get('doc_host') or cfg.get('git_url')

    reqs = ['pip', 'python', 'packaging']
    if cfg.get('requirements'): reqs += cfg.get('requirements').split()
    if cfg.get('conda_requirements'): reqs += cfg.get('conda_requirements').split()

    pypi = pypi_json(f'{name}/{ver}')
    rel = [o for o in pypi['urls'] if o['packagetype']=='sdist'][0]

    # Work around conda build bug - 'package' and 'source' must be first
    d1 = {
        'package': {'name': name, 'version': ver},
        'source': {'url':rel['url'], 'sha256':rel['digests']['sha256']}
    }

    d2 = {
        'build': {'number': '0', 'noarch': 'python',
                  'script': '{{ PYTHON }} -m pip install . -vv'},
        'requirements': {'host':reqs, 'run':reqs},
        'test': {'imports': ['numpy', name]},
        'about': {
            'license': 'Apache Software',
            'license_family': 'APACHE',
            'home': url, 'doc_url': url, 'dev_url': url,
            'summary': cfg.get('description')
        },
        'extra': {'recipe-maintainers': [cfg.get('user')]}
    }
    return name,d1,d2

# Cell
def write_conda_meta(path='conda'):
    "Writes a `meta.yaml` file to the `conda` directory of the current directory"
    _write_yaml(path, *_get_conda_meta())