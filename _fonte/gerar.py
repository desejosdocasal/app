# Monta o app a partir de _fonte/: junta as cartas em cartas.js e gera uma cópia do app em cada pasta de acesso.
# O acesso vai no CAMINHO (nunca na query): a query some quando a pessoa instala o PWA e ela perde o que comprou.
#   python _fonte/gerar.py
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(AQUI)

# pasta -> o que ela libera. Cada compra leva ao link da sua pasta; o aparelho soma tudo o que já abriu.
PASTAS = {
    'a7k2qm': ['base'],                                  # front
    'p9x4re': ['base', 'proibido'],                      # bump Nível Proibido
    'd3n8tw': ['base', 'datas'],                         # bump Datas Especiais
    'u6h1vz': ['base', 'pro'],                           # upsell Desejos Pro
    't5w9ck': ['base', 'proibido', 'datas', 'pro'],      # teste interno: tudo liberado
}
# links de checkout dos pacotes (preencher quando o checkout existir)
CHECKOUT = {'proibido': '#', 'datas': '#', 'pro': '#'}
VERSAO = 1

def ler(n):
    return json.load(open(os.path.join(APP, 'conteudo', n), encoding='utf-8'))

vd1, vd2, rdm, qdp = ler('vd-leve-romantico.json'), ler('vd-picante-semcensura.json'), ler('roleta-dados-match.json'), ler('quiz-datas-pro.json')
cartas = {
    'vd': {**vd1, **vd2},
    'roleta': rdm['roleta'], 'dados': rdm['dados'], 'match': rdm['match'],
    'quiz': qdp['quiz'], 'datas': qdp['datas'], 'fantasia': qdp['fantasia'], 'noites': qdp['noites'], 'distancia': qdp['distancia'],
}
with open(os.path.join(APP, 'cartas.js'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('/* gerado por _fonte/gerar.py a partir de conteudo/ */\nwindow.CARTAS=' + json.dumps(cartas, ensure_ascii=False, separators=(',', ':')) + ';\n')

modelo = open(os.path.join(AQUI, 'app.html'), encoding='utf-8').read()

def pagina(acesso, raiz):
    s = modelo.replace('__ACESSO__', json.dumps(acesso)).replace('__RAIZ__', raiz)
    for k, v in CHECKOUT.items():
        s = s.replace(f'__CK_{k.upper()}__', v)
    assert '__' not in re.sub(r'window\.__prompt', '', s), 'sobrou marcador no modelo'
    return s

def manifesto(pasta):
    return {
        'name': 'Desejos do Casal', 'short_name': 'Desejos', 'lang': 'pt-BR',
        'description': 'Jogos para casal: verdade ou desafio, roleta, dados e match de desejos.',
        'start_url': './', 'scope': '../', 'display': 'standalone', 'orientation': 'portrait',
        'background_color': '#12060b', 'theme_color': '#12060b',
        'icons': [
            {'src': '../img/icones/icone-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': '../img/icones/icone-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {'src': '../img/icones/icone-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
        ],
    }

# raiz: sem acesso (mostra o aviso de abrir pelo link do e-mail, a não ser que o aparelho já tenha acesso guardado)
open(os.path.join(APP, 'index.html'), 'w', encoding='utf-8', newline='\n').write(pagina([], './'))
json.dump(manifesto('.') | {'start_url': './', 'scope': './'}, open(os.path.join(APP, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for pasta, acesso in PASTAS.items():
    os.makedirs(os.path.join(APP, pasta), exist_ok=True)
    open(os.path.join(APP, pasta, 'index.html'), 'w', encoding='utf-8', newline='\n').write(pagina(acesso, '../'))
    json.dump(manifesto(pasta), open(os.path.join(APP, pasta, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

sw = open(os.path.join(AQUI, 'sw.js'), encoding='utf-8').read()
sw = sw.replace('__VERSAO__', str(VERSAO)).replace('__PASTAS__', json.dumps(list(PASTAS)))
open(os.path.join(APP, 'sw.js'), 'w', encoding='utf-8', newline='\n').write(sw)
open(os.path.join(APP, '.nojekyll'), 'w').close()
total = sum(len(v) if isinstance(v, list) else sum(len(x) if isinstance(x, list) else sum(len(y) for y in x.values()) for x in v.values()) for v in cartas.values())
print('ok:', len(PASTAS), 'pastas, cartas.js com', os.path.getsize(os.path.join(APP, 'cartas.js')) // 1024, 'KB, versão', VERSAO)
