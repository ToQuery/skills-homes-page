import json
import os
import shutil

# Configuration
TEMPLATE_FILE = 'scripts/template.html'
LOCALES_FILE = 'scripts/locales.json'
OUTPUT_DIR = 'docs'

import datetime

# ... (Previous constants)
HOSTNAME = "https://skills.homes"

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
            path_prefix = "./"
            # For sitemap, we use relative URL from root
            url = "/index.html"
        else:
            output_path = os.path.join(OUTPUT_DIR, lang, 'index.html')
            path_prefix = "../"
            url = f"/{lang}/index.html"
        
        # Replace placeholders
        content = template
        
        # Inject computed path_prefix
        content = content.replace("{{ path_prefix }}", path_prefix)

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

    print("Build complete.")

if __name__ == "__main__":
    main()
