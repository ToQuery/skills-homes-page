import json
import os
import shutil

# Configuration
TEMPLATE_FILE = 'scripts/template.html'
LOCALES_FILE = 'scripts/locales.json'
OUTPUT_DIR = 'docs'

import datetime

import argparse

# ... (Previous constants)
DEFAULT_DOMAIN = "https://toquery.github.io"
DEFAULT_URI_PREFIX = "/skills-homes-page"

def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_file(filepath, content):
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated: {filepath}")

def main():
    parser = argparse.ArgumentParser(description='Build Skills.Homes static site.')
    parser.add_argument('--domain', help='Domain for sitemap and robots.txt (e.g., https://example.com)')
    parser.add_argument('--uri-prefix', help='URI prefix for links (e.g., /repo-name)')

    args = parser.parse_args()

    # Precedence: CLI Args > Env Vars > Defaults
    # We use (val is not None) check to allow explicit empty strings ("")

    if args.domain is not None:
        domain = args.domain
    else:
        domain = os.getenv("DOMAIN", DEFAULT_DOMAIN)

    if args.uri_prefix is not None:
        uri_prefix = args.uri_prefix
    else:
        uri_prefix = os.getenv("URI_PREFIX", DEFAULT_URI_PREFIX)

    # Ensure uri_prefix starts with / if not empty and not http(s)
    if uri_prefix and not uri_prefix.startswith('/') and not uri_prefix.startswith('http'):
         uri_prefix = '/' + uri_prefix

    print(f"Using Domain: {domain}")
    print(f"Using URI Prefix: {uri_prefix}")

    # Load template and locales
    template = load_file(TEMPLATE_FILE)
    locales = json.loads(load_file(LOCALES_FILE))

    print(f"Loaded {len(locales)} languages.")

    sitemap_urls = []
    current_date = datetime.date.today().isoformat()
    DEFAULT_LANG = 'en'

    for lang, data in locales.items():

        # Determine output path, URL, and path_prefix
        if lang == DEFAULT_LANG:
            output_path = os.path.join(OUTPUT_DIR, 'index.html')
            # For sitemap, we use absolute URL
            url = f"{domain}{uri_prefix}/index.html"
        else:
            output_path = os.path.join(OUTPUT_DIR, lang, 'index.html')
            url = f"{domain}{uri_prefix}/{lang}/index.html"

        # Clean up double slashes in URL if any (except protocol)
        # url = re.sub(r'(?<!:)//', '/', url)

        # Replace placeholders
        content = template

        # Inject computed seo_canonical
        content = content.replace("{{ seo_canonical }}", f"{domain}{uri_prefix}/index.html")

        # Inject computed uri_prefix
        content = content.replace("{{ domain }}", domain)
        content = content.replace("{{ uri_prefix }}", uri_prefix)

        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"
            content = content.replace(placeholder, value)


        save_file(output_path, content)
        sitemap_urls.append((url, current_date))

    # Generate Sitemap
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url, lastmod in sitemap_urls:
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{url}</loc>\n'
        sitemap_content += f'    <lastmod>{lastmod}</lastmod>\n'
        sitemap_content += '    <changefreq>weekly</changefreq>\n'
        sitemap_content += '    <priority>0.8</priority>\n'
        sitemap_content += '  </url>\n'

    sitemap_content += '</urlset>'

    save_file(os.path.join(OUTPUT_DIR, 'sitemap.xml'), sitemap_content)
    print("Sitemap generated.")

    # Generate robots.txt
    robots_content = f"User-agent: *\nAllow: /\n\nSitemap: {domain}{uri_prefix}/sitemap.xml\n"
    save_file(os.path.join(OUTPUT_DIR, 'robots.txt'), robots_content)
    print("robots.txt generated.")

    print("Build complete.")

if __name__ == "__main__":
    main()
