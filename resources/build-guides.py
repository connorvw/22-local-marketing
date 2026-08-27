import base64, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {
    'sora-regular': r'C:\22 Local Marketing\proposals\site\moberlys-tree-service-0c8d\assets\Sora-Regular.ttf',
    'sora-bold': r'C:\22 Local Marketing\logo-kit\fonts\Sora-Bold.ttf',
    'sora-xbold': r'C:\22 Local Marketing\logo-kit\fonts\Sora-ExtraBold.ttf',
}
LOGO = r'C:\22 Local Marketing\logo-kit\all-formats-no-margin\png\22lm-primary-tight.png'

GUIDES = {
    'review-management-guide': '22LM Review Management Guide',
    'photo-optimization-guide': '22LM Photo Optimization Guide',
    'gbp-optimization-checklist': '22LM GBP Optimization Checklist',
    'tree-care-citations-list': '22LM Tree Care Citations List',
}

logo_b64 = base64.b64encode(open(LOGO, 'rb').read()).decode()
font_b64 = {k: base64.b64encode(open(p, 'rb').read()).decode() for k, p in FONTS.items()}

for slug, title in GUIDES.items():
    folder = os.path.join(HERE, slug)
    src = os.path.join(folder, slug + '.html')
    h = open(src, encoding='utf-8').read()
    for k, b in font_b64.items():
        h = h.replace('{{FONT:' + k + '}}', b)
    h = h.replace('{{LOGO_B64}}', logo_b64)
    final = os.path.join(folder, slug + '-final.html')
    open(final, 'w', encoding='utf-8').write(h)
    pdf = os.path.join(folder, title + '.pdf')
    r = subprocess.run([sys.executable, r'C:\Agency Operations\agent\html2pdf.py', '--html', final, '--out', pdf], capture_output=True, text=True)
    print(slug, '->', r.stdout.strip() or r.stderr.strip())
