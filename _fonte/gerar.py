# Monta o app a partir de _fonte/, num idioma: junta as cartas em cartas.js e gera uma cópia do app em cada pasta de acesso.
# O acesso vai no CAMINHO (nunca na query): a query some quando a pessoa instala o PWA e ela perde o que comprou.
# Um código só para todos os países: o que muda é o texto da tela (_fonte/textos/<lingua>.json) e as cartas
# (conteudo/<lingua>/). Correção no app vale para todos os idiomas de uma vez.
#   python _fonte/gerar.py                   Brasil, aqui mesmo (repositório desejosdocasal/app)
#   python _fonte/gerar.py --lingua it-IT    Itália, em ../app-it (o repositório italiano)
import argparse, json, os, re, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)

LINGUAS = {
    'pt-BR': os.path.join(APP),
    'it-IT': os.path.join(os.path.dirname(APP), 'app-it'),
}
ap = argparse.ArgumentParser()
ap.add_argument('--lingua', default='pt-BR', choices=list(LINGUAS))
LINGUA = ap.parse_args().lingua
SAIDA = LINGUAS[LINGUA]

# pasta -> o que ela libera. Cada compra leva ao link da sua pasta; o aparelho soma tudo o que já abriu.
PASTAS = {
    'a7k2qm': ['base'],                                  # front
    'p9x4re': ['base', 'proibido'],                      # bump Sem Censura
    'd3n8tw': ['base', 'datas'],                         # bump Datas Especiais
    'u6h1vz': ['base', 'pro'],                           # upsell Pro
    't5w9ck': ['base', 'proibido', 'datas', 'pro'],      # teste interno: tudo liberado
}
# links de checkout dos pacotes, por idioma (preencher quando o checkout existir)
CHECKOUT = {
    'pt-BR': {'proibido': '#', 'datas': '#', 'pro': '#'},
    # Itália: as ofertas "dentro do app" da Cakto (Senza Censura a 12,90 €, Occasioni a 4,90 €, Pro a 19,90 €, total com a comissão)
    'it-IT': {'proibido': 'https://pay.cakto.com.br/9tf957m', 'datas': 'https://pay.cakto.com.br/3cwt22p', 'pro': 'https://pay.cakto.com.br/ufkhv67'},
}[LINGUA]
VERSAO = 4

L = json.load(open(os.path.join(AQUI, 'textos', LINGUA + '.json'), encoding='utf-8'))

# as cartas do idioma: os arquivos vd-* formam o Verdade ou Desafio, os outros trazem cada jogo pela chave
pasta_cartas = os.path.join(APP, 'conteudo', LINGUA)
cartas = {'vd': {}}
for n in sorted(os.listdir(pasta_cartas)):
    if not n.endswith('.json'):
        continue
    j = json.load(open(os.path.join(pasta_cartas, n), encoding='utf-8'))
    (cartas['vd'] if n.startswith('vd-') else cartas).update(j)
falta = {'roleta', 'dados', 'match', 'quiz', 'datas', 'fantasia', 'noites', 'distancia'} - set(cartas)
falta |= {'leve', 'romantico', 'picante', 'proibido'} - set(cartas['vd'])
assert not falta, f'faltam cartas em conteudo/{LINGUA}: {sorted(falta)}'

os.makedirs(SAIDA, exist_ok=True)
with open(os.path.join(SAIDA, 'cartas.js'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(f'/* gerado por _fonte/gerar.py a partir de conteudo/{LINGUA}/ */\nwindow.CARTAS=' + json.dumps(cartas, ensure_ascii=False, separators=(',', ':')) + ';\n')

modelo = open(os.path.join(AQUI, 'app.html'), encoding='utf-8').read()

def pagina(acesso, raiz):
    s = (modelo.replace('__ACESSO__', json.dumps(acesso)).replace('__RAIZ__', raiz)
         .replace('__TEXTOS__', json.dumps(L, ensure_ascii=False)).replace('__LANG__', L['lang']).replace('__CURTO__', L['curto']))
    for k, v in CHECKOUT.items():
        s = s.replace(f'__CK_{k.upper()}__', v)
    assert '__' not in re.sub(r'window\.__prompt', '', s), 'sobrou marcador no modelo'
    return s

def manifesto(pasta):
    return {
        'name': L['marca'], 'short_name': L['curto'], 'lang': L['lang'],
        'description': L['manifesto'],
        'start_url': './', 'scope': '../', 'display': 'standalone', 'orientation': 'portrait',
        'background_color': '#12060b', 'theme_color': '#12060b',
        'icons': [
            {'src': '../img/icones/icone-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': '../img/icones/icone-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': '../img/icones/icone-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }

# raiz: sem acesso (mostra o aviso de abrir pelo link do e-mail, a não ser que o aparelho já tenha acesso guardado)
open(os.path.join(SAIDA, 'index.html'), 'w', encoding='utf-8', newline='\n').write(pagina([], './'))
json.dump(manifesto('.') | {'start_url': './', 'scope': './'}, open(os.path.join(SAIDA, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for pasta, acesso in PASTAS.items():
    os.makedirs(os.path.join(SAIDA, pasta), exist_ok=True)
    open(os.path.join(SAIDA, pasta, 'index.html'), 'w', encoding='utf-8', newline='\n').write(pagina(acesso, '../'))
    json.dump(manifesto(pasta), open(os.path.join(SAIDA, pasta, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

sw = open(os.path.join(AQUI, 'sw.js'), encoding='utf-8').read()
sw = sw.replace('__VERSAO__', str(VERSAO)).replace('__PASTAS__', json.dumps(list(PASTAS)))
open(os.path.join(SAIDA, 'sw.js'), 'w', encoding='utf-8', newline='\n').write(sw)
open(os.path.join(SAIDA, '.nojekyll'), 'w').close()

# fora do Brasil o app mora em outro repositório: leva as imagens que o app usa e a regra da pasta de teste
if SAIDA != APP:
    for sub, filtro in (('icones', lambda n: n.endswith('.png')), ('marca', lambda n: n.endswith('.webp'))):
        os.makedirs(os.path.join(SAIDA, 'img', sub), exist_ok=True)
        for n in os.listdir(os.path.join(APP, 'img', sub)):
            if filtro(n):
                shutil.copy2(os.path.join(APP, 'img', sub, n), os.path.join(SAIDA, 'img', sub, n))
    open(os.path.join(SAIDA, '.gitignore'), 'w', encoding='utf-8', newline='\n').write(
        '# pasta de teste interno com tudo liberado: só local, nunca no ar\nt5w9ck/\n')

total = sum(len(v) if isinstance(v, list) else sum(len(x) if isinstance(x, list) else sum(len(y) for y in x.values()) for x in v.values()) for v in cartas.values())
print('ok:', LINGUA, '->', os.path.relpath(SAIDA, os.path.dirname(APP)), '|', len(PASTAS), 'pastas, cartas.js com', os.path.getsize(os.path.join(SAIDA, 'cartas.js')) // 1024, 'KB, versão', VERSAO)
