#!/usr/bin/env python3
"""Extract public download metadata without fetching hosted files or running site code."""
import argparse, base64, hashlib, ipaddress, json, re, socket, time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
HOSTS = {'1fichier.com','mediafire.com','akirabox.com','akirabox.to','vikingfile.com','ranoz.gg','uploadnow.io','mega.nz','mega.co.nz','drive.google.com','gofile.io','rootz.so','1cloudfile.com','buzzheavier.com'}
CONTAINERS = {'filecrypt.cc','filecrypt.co'}
SHORTENERS = {'clk.sh','bit.ly','goo.gl'}
ARCHIVES = {'downloadgameps3.net','www.downloadgameps3.net'}

def host(url):
    return (urlsplit(url).hostname or '').lower().removeprefix('www.')

def public_url(url):
    p = urlsplit(url)
    if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:
        raise ValueError('URL HTTP(S) pública sem credenciais exigida')
    for addr in socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme=='https' else 80), type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(addr[4][0]).is_global:
            raise ValueError('Destino de rede não público recusado')

def text(node):
    return node.get_text(' ',strip=True) if node else ''

def kind(label):
    if re.match(r'(?i)^update\b',label): return 'atualização'
    if re.match(r'(?i)^DLC\b',label): return 'DLC'
    if re.match(r'(?i)^(game|base game)\b',label): return 'jogo base'
    return 'não identificado'

def unpack(soup):
    for n in list(soup.select('.secure-data[data-payload]')):
        try:
            decoded = base64.b64decode(n['data-payload'],validate=True).decode('utf-8')
            if '<' not in decoded: raise ValueError('payload não contém HTML')
            n.clear(); n.append(BeautifulSoup(decoded,'html.parser')); n['data-decoded']='base64 UTF-8'
        except (ValueError,UnicodeError) as e:
            n['data-error']=str(e)
    return soup

def known_wrapper(url):
    # Supported because the captured clk.sh script explicitly encodes original href as Base64 in url=.
    p=urlsplit(url)
    if host(url)=='clk.sh' and p.path.rstrip('/')=='/full':
        value=parse_qs(p.query).get('url',[''])[0]
        try:
            result=base64.b64decode(value,validate=True).decode('utf-8')
            if urlsplit(result).scheme in ('http','https'):
                return result,'clk.sh/full: parâmetro url em Base64 (formato confirmado no script público)'
        except (ValueError,UnicodeError): pass
    return url,None

def link_record(a,base):
    original=urljoin(base,a.get('href',''))
    url,evidence=known_wrapper(original)
    if urlsplit(url).scheme not in ('http','https'): return None
    h=host(url)
    typ='arquivo/pasta de hospedagem' if h in HOSTS else 'container' if h in CONTAINERS else 'página de links' if h in ARCHIVES and re.match(r'^/archives/\d+/?$',urlsplit(url).path) else 'encurtador' if h in SHORTENERS else 'outro'
    label=text(a)
    parent=a.find_parent(['p','li','tr']) or a.parent
    context=text(parent)
    part=re.search(r'(?i)(?:part[ ._-]*|\.r)(\d+)', label+' '+url)
    return {'label':label,'url':url,'original_url':original,'type':typ,'context':context,'part':int(part[1]) if part else None,'decoding_evidence':evidence,'attributes':dict(a.attrs)}

def parse_options(html,url):
    soup=BeautifulSoup(html,'html.parser')
    root=soup.select_one('.entry-content') or soup.select_one('article') or soup
    title=text(soup.select_one('h1')) or text(soup.title)
    options=[]
    for index,spoiler in enumerate(root.select('.su-spoiler'),1):
        button=text(spoiler.select_one('.su-spoiler-title'))
        if not re.search(r'(?i)link\s+(download|mirror)',button): continue
        heading=''
        for prev in spoiler.previous_siblings:
            if getattr(prev,'name',None) and re.search(r'\bCUSA\d+\b',text(prev)) and 'su-spoiler' not in prev.get('class',[]):
                heading=text(prev); break
        original=str(spoiler)
        decoded=unpack(BeautifulSoup(original,'html.parser'))
        body=decoded.select_one('.su-spoiler-content') or decoded
        rows=[]; ancillary=[]
        for p in body.find_all(['p','li','tr']):
            links=[r for a in p.select('a[href]') if (r:=link_record(a,url))]
            if not links: continue
            label=text(p).split(':',1)[0].strip()
            item={'label':label,'kind':kind(label),'context':text(p),'version':(m[1] if (m:=re.search(r'(?i)update\s+([0-9.]+)',label)) else None),'links':links}
            (rows if item['kind']!='não identificado' else ancillary).append(item)
        cusas=list(dict.fromkeys(re.findall(r'\bCUSA\d+\b',heading or text(body))))
        region=re.search(r'\b(EUR|USA|JPN|ASIA)\b',heading or text(body))
        version=re.search(r'\bv([\d.]+)',heading)
        options.append({'index':index,'edition':heading,'cusa':cusas,'region':region[1] if region else None,'version':version[1] if version else None,'button':button,'evidence':{'source_url':url,'selector':f'.su-spoiler (posição {index})','encoding':'data-payload Base64 UTF-8' if 'data-payload=' in original else 'HTML direto','errors':[n.get('data-error') for n in decoded.select('[data-error]')]},'notes':text(body),'components':rows,'ancillary':ancillary})
    return {'source_url':url,'title':title,'options':options}

class Client:
    def __init__(self,cache=ROOT/'cache',timeout=20,interval=1,max_redirects=8,ttl=86400):
        self.cache=Path(cache); self.cache.mkdir(parents=True,exist_ok=True)
        self.timeout=timeout;self.interval=interval;self.max_redirects=max_redirects;self.ttl=ttl;self.last=0
        self.session=requests.Session();self.session.headers['User-Agent']='PublicLinkResolver/1.0 (metadata only)'
    def one(self,url):
        public_url(url)
        key=hashlib.sha256(url.encode()).hexdigest(); path=self.cache/(key+'.json')
        if path.exists():
            data=json.loads(path.read_text(encoding='utf-8'))
            if time.time()-data['fetched_at']<self.ttl:
                return dict(data,cached=True)
        time.sleep(max(0,self.interval-(time.monotonic()-self.last)))
        self.last=time.monotonic()
        with self.session.get(url,timeout=self.timeout,allow_redirects=False,stream=True) as r:
            headers=dict(r.headers); mime=r.headers.get('Content-Type','').lower()
            result={'url':url,'status':r.status_code,'location':r.headers.get('Location'),'headers':headers,'fetched_at':time.time(),'body':'','cached':False}
            if r.headers.get('Content-Disposition') or (r.status_code not in (301,302,303,307,308) and not any(t in mime for t in ['text/html','application/xhtml+xml','text/plain','application/json'])):
                result['blocked']='Resposta de arquivo ou tipo não textual: corpo não lido'
            elif r.status_code not in (301,302,303,307,308):
                chunks=[]; size=0
                for chunk in r.iter_content(16384):
                    size+=len(chunk)
                    if size>3_000_000: raise ValueError('HTML excede limite de 3 MB')
                    chunks.append(chunk)
                result['body']=b''.join(chunks).decode(r.encoding or 'utf-8',errors='replace')
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        return result
    def trace(self,url):
        chain=[];seen=set()
        for _ in range(self.max_redirects+1):
            if url in seen: return {'chain':chain,'final_url':url,'error':'Loop de redirecionamento'}
            seen.add(url)
            # Never request hosting, container or file URLs, even if a redirect points there.
            if host(url) in HOSTS|CONTAINERS or re.search(r'(?i)\.(pkg|zip|rar|7z|iso)(?:$|[?#])',url):
                return {'chain':chain,'final_url':url,'stopped':'Hospedagem/arquivo/container: não acessado','body':''}
            try: r=self.one(url)
            except (requests.RequestException,ValueError,OSError) as e: return {'chain':chain,'final_url':url,'error':str(e),'body':''}
            chain.append({k:r.get(k) for k in ('url','status','location','cached','fetched_at')})
            body=r['body']; soup=BeautifulSoup(body,'html.parser')
            if r['status']>=400 or r.get('blocked'):
                return {'chain':chain,'final_url':url,'error':r.get('blocked') or ('Cloudflare: desafio JavaScript/cookies' if 'Just a moment' in body or '_cf_chl_opt' in body else f'HTTP {r["status"]}'),'body':body}
            if re.search(r'(?i)please (?:click on below|complete|solve).{0,40}captcha',text(soup)):
                return {'chain':chain,'final_url':url,'error':'CAPTCHA exige interação; formulário não enviado','body':body}
            nxt=r.get('location') if r['status'] in (301,302,303,307,308) else None
            mechanism='HTTP Location'
            if not nxt:
                meta=soup.find('meta',attrs={'http-equiv':re.compile('^refresh$',re.I)})
                if meta and (m:=re.search(r'(?i)url\s*=\s*(.+)',meta.get('content',''))): nxt=m[1].strip(' \"\'');mechanism='meta refresh'
            if not nxt:
                # Only literal script assignments; never evaluate JavaScript or guess computed URLs.
                for script in soup.find_all('script'):
                    m=re.fullmatch(r'''\s*(?:window\.)?location(?:\.href)?\s*=\s*['"](https?://[^'"\s]+)['"]\s*;?\s*''',script.get_text())
                    if m: nxt=m[1];mechanism='JavaScript literal (sem execução)';break
            if not nxt: return {'chain':chain,'final_url':url,'body':body,'unhandled_scripts':bool(soup.find('script'))}
            chain[-1]['redirect_mechanism']=mechanism
            url=urljoin(url,nxt)
        return {'chain':chain,'final_url':url,'error':'Limite de redirecionamentos','body':''}

def resolve(url,client):
    source=client.trace(url); html=source.pop('body','')
    result=parse_options(html,source['final_url'])
    result['requested_url']=url;result['source_trace']=source;result['destinations']={}
    if source.get('error'):result['error']=source['error']
    if not result['options']:result['warning']='Nenhuma opção reconhecida; nenhum destino foi deduzido.'
    for option in result['options']:
        for component in option['components']:
            for link in component['links']:
                link['association']='confirmada na origem: botão → linha do componente → href'
                if link['type'] not in ('página de links','encurtador'):continue
                target=link['url']
                if target in result['destinations']:continue
                trace=client.trace(target);body=trace.pop('body','');s=unpack(BeautifulSoup(body,'html.parser'))
                content=s.select_one('.entry-content') or s.select_one('article') or s
                links=[r for a in content.select('a[href]') if (r:=link_record(a,trace['final_url'])) and r['type'] in ('arquivo/pasta de hospedagem','container')]
                for order,r in enumerate(links,1):r['document_order']=order
                # Identity is separate from the explicit association established by source href.
                found_cusa=[c for c in option['cusa'] if c in text(content)]
                trace.update(title=text(s.title),identity_evidence={'matching_cusa':found_cusa},identity_status='CUSA encontrado no conteúdo' if found_cusa else 'identidade não corroborada no destino',links=links)
                trace['resolution_status']='bloqueado' if trace.get('error') else 'links extraídos; identidade a conferir' if links else 'não resolvido: nenhum link de hospedagem recuperado'
                result['destinations'][target]=trace
    return result

def render(r):
    out=[r['title'],r['source_url']]
    if r.get('error'):out.append('ERRO: '+r['error'])
    if r.get('warning'):out.append(r['warning'])
    for o in r['options']:
        out.append(f'\n[{o["index"]}] {o["edition"]} | {o["button"]} | {o["evidence"]["encoding"]}')
        for c in o['components']:
            out.append('  '+c['label']+' ['+c['kind']+']')
            for l in c['links']:
                out.append(f'    {l["label"]}: {l["url"]} ({l["type"]}; associação confirmada no HTML da origem)')
                if (d:=r['destinations'].get(l['url'])):
                    out.append('      '+(d.get('error') or d['resolution_status']+'; '+d['identity_status']))
                    for h in d['links']:out.append(f'      #{h["document_order"]} parte={h["part"]}: {h["label"]} {h["url"]}')
    return '\n'.join(out)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('url');p.add_argument('--json',metavar='ARQUIVO',help='Exportar JSON; use - para stdout');p.add_argument('--cache',type=Path,default=ROOT/'cache');p.add_argument('--timeout',type=float,default=20);p.add_argument('--interval',type=float,default=1);p.add_argument('--max-redirects',type=int,default=8);p.add_argument('--refresh',action='store_true')
    a=p.parse_args()
    if a.timeout<=0 or a.interval<0 or not 0<=a.max_redirects<=30:p.error('timeout > 0, interval >= 0, max-redirects entre 0 e 30')
    result=resolve(a.url,Client(a.cache,a.timeout,a.interval,a.max_redirects,0 if a.refresh else 86400))
    data=json.dumps(result,ensure_ascii=False,indent=2)
    if a.json=='-':print(data)
    else:
        print(render(result))
        if a.json:Path(a.json).write_text(data+'\n',encoding='utf-8')
    return 2 if result.get('error') or not result['options'] else 0

if __name__=='__main__':raise SystemExit(main())
