"""One-time vendoring of versioned public icons and a preview-only GitHub stylesheet."""
from pathlib import Path
from urllib.request import urlopen
ROOT = Path(__file__).resolve().parents[1]
ICONS = {'python':'original', 'typescript':'original', 'javascript':'original', 'java':'original', 'nodejs':'original', 'fastapi':'original', 'graphql':'plain', 'postgresql':'original', 'amazonwebservices':'original-wordmark', 'docker':'original', 'kubernetes':'plain', 'terraform':'original', 'pytorch':'original', 'sqlite':'original'}
def download(url, destination):
    with urlopen(url, timeout=40) as response:
        body = response.read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)
for name, variant in ICONS.items():
    download(f'https://raw.githubusercontent.com/devicons/devicon/v2.17.0/icons/{name}/{name}-{variant}.svg', ROOT / f'assets/icons/{name}.svg')
download('https://raw.githubusercontent.com/devicons/devicon/v2.17.0/LICENSE', ROOT / 'assets/icons/LICENSE')
download('https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown.css', ROOT / '.preview/github-markdown.css')
print('Vendored icons and preview stylesheet')
