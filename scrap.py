from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from tqdm import tqdm

def processa_site(nome_site, secao=None, assunto=None, limite_artigos=100):
    '''Faz o webscraping de um determinado site'''
    if nome_site == 'tercalivre':
        if secao and assunto:
            scraped_site = scrap_tercalivre(f'https://tercalivre.com.br/{secao}/{assunto}/', f'https://tercalivre.com.br/{secao}/{assunto}/page', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-{secao}-{assunto}-sites.json')
            scraped_pages = scrap_tercalivre_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}-{secao}-{assunto}.json') 
    elif nome_site == '247':
        if secao and assunto:
            scraped_site = scrap_247(f'https://www.brasil247.com/{assunto}', f'https://www.brasil247.com/{assunto}?page=', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-{secao}-{assunto}-sites.json')
            scraped_pages = scrap_247_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}-{secao}-{assunto}.json') 
    elif nome_site == 'conexaopolitica':
        if secao and assunto:
            scraped_site = scrap_conexaopolitica(f'https://conexaopolitica.com.br/{secao}/{assunto}', f'https://conexaopolitica.com.br/{secao}/{assunto}/page', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-{secao}-{assunto}-sites.json')
            scraped_pages = scrap_conexaopolitica_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}-{secao}-{assunto}.json')        
    elif nome_site == 'republica':
            scraped_site = scrap_republica(f'https://republicadecuritiba.net', f'https://republicadecuritiba.net/page', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-sites.json')
            scraped_pages = scrap_republica_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}.json')    
    elif nome_site == 'senso':
        if secao:
            scraped_site = scrap_senso(f'https://sensoincomum.org/{secao}', f'https://sensoincomum.org/category/{secao}/page/', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-{secao}-sites.json')
            scraped_pages = scrap_senso_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}-{secao}.json')   
    elif nome_site == 'dcm':
            scraped_site = scrap_dcm(f'https://www.diariodocentrodomundo.com.br', f'https://www.diariodocentrodomundo.com.br/page/', limite_artigos)
            exporta_json(scraped_site, f'{nome_site}-sites.json')
            scraped_pages = scrap_dcm_conteudo(scraped_site)
            exporta_json(scraped_pages, f'{nome_site}.json')                                       

def exporta_json(lista_noticias, nome_arquivo):
    with open('TCC/data/' + nome_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(lista_noticias , arquivo, indent=4, ensure_ascii=False)

def importa_json(nome_arquivo):
    with open('TCC/data/' + nome_arquivo, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

def remove_tags(texto):
    """Remove tags html de um texto"""
    import re
    limpo = re.compile('<.*?>')
    sem_tags = re.sub(limpo, '', texto)
    return sem_tags.replace('&nbsp', '') 

def encontra_elemento_clicavel(elemento_pai, atributo, estrategia, timeout=10):
    if timeout == 0 : return False
    try: 
        elemento = WebDriverWait(elemento_pai, timeout).until(
        EC.element_to_be_clickable((estrategia, atributo))        )
        time.sleep(1)
        return elemento
    except:
        print(f'\nTimeout em\'{atributo}\'')
        return False

def encontra_elemento_visivel(elemento_pai, atributo, estrategia, timeout=10):
    try: 
        elementos = WebDriverWait(elemento_pai, timeout).until(
                    EC.visibility_of_all_elements_located((estrategia, atributo)))
        if len(elementos) > 1:
            return elementos
        else:
            return elementos[0]    
    except:
        print(f'\nTimeout em\'{atributo}\'')
        return False       

def encontra_elemento(elemento_pai, atributo, estrategia, timeout=10):
    try: 
        elementos = WebDriverWait(elemento_pai, timeout).until(
                    EC.invisibility_of_element((estrategia, atributo))
        )
        if len(elementos) > 1:
            return elementos
        else:
            return elementos[0]    
    except:
        print(f'\nTimeout em\'{atributo}\'')
        return False       


def aguarda(intervalo):
    time.sleep(intervalo)

def scrap_tercalivre(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []
   
    n_pagina = 18 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}/{n}/'
            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '//*[@id="content"]/div/div/div[1]/div[2]', By.XPATH)
            
            artigos = encontra_elemento_visivel(painel_artigos, '//h2/a', By.XPATH)
            
            if not artigos or (not isinstance(artigos, list)):
                ultima = encontra_elemento_visivel(driver, '#content > div > article > div > div > div.herald-ovrld > header > h1', By.CSS_SELECTOR)
                if ultima.text == 'Página não encontrada!': break
                continue
        except:
            continue    

        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
 
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    return(lista_noticias)

def scrap_tercalivre_conteudo(lista_artigos):
    driver.set_page_load_timeout(5)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '/html/body/div[4]/div[1]/article/div/div[1]/div[2]/div[2]', By.XPATH, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('div/p')   
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:  
                texto.append(p.get_attribute('innerHTML')) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass
    return lista_paginas

def scrap_tercalivre_colunistas(url):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_colunistas = []
    painel_colunistas = encontra_elemento_visivel(driver, '/html/body/div[4]/div[2]/div/div/div/div[1]/div[2]', By.XPATH)
    colunistas = painel_colunistas.find_elements_by_xpath('//h3/a')
    
    for colunista in colunistas:
        link = colunista.get_attribute('href')
        lista_colunistas.extend(link.split('/')[-2:-1])
    return(lista_colunistas)

def scrap_conexaopolitica(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []
   
    n_pagina = 10 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}/{n}/'
            driver.get(f'{nova_pagina}')
            aguarda(0.5)
            painel_artigos = driver.find_element_by_css_selector('#mvp-main-body-wrap > div.mvp-main-blog-wrap.left.relative > div > div > div')
            artigos = painel_artigos.find_elements_by_xpath('//li[contains(@class, "mvp-blog-story-col left relative infinite-post")]/a')
            if not artigos or (not isinstance(artigos, list)):
                ultima = encontra_elemento_visivel(driver, '#mvp-404 > h1', By.CSS_SELECTOR)
                
                if 'Error' in ultima.text: 
                    break
                continue
        except:
            break

        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    
    return(lista_noticias)

def scrap_conexaopolitica_conteudo(lista_artigos):
    driver.set_page_load_timeout(5)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '//*[@id="mvp-content-main"]', By.XPATH, 3)
        try:
            if painel_paragrafos: 
                paragrafos = painel_paragrafos.find_elements_by_tag_name('p')   
            else:
                paragrafos = False
            if not paragrafos:
                print('\nNenhum paragrafo')
                continue
            texto = []
            for p in paragrafos:  
                texto.append(p.get_attribute('innerHTML')) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass
    return lista_paginas

def scrap_conexaopolitica_colunistas(url):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_colunistas = []
    painel_colunistas = encontra_elemento_visivel(driver, '/html/body/div[4]/div[2]/div/div/div/div[1]/div[2]', By.XPATH)
    colunistas = painel_colunistas.find_elements_by_xpath('//h3/a')
    
    for colunista in colunistas:
        link = colunista.get_attribute('href')
        lista_colunistas.extend(link.split('/')[-2:-1])
    return(lista_colunistas)
    
def scrap_247(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []
    limite_timeout = 0
    n_pagina = 21 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}{n}'
            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '/html/body/main/div[3]/div[1]/div/div[1]/div', By.XPATH)
            artigos = encontra_elemento_visivel(painel_artigos, '//div[1]/h3/a', By.XPATH)
            if not artigos or (not isinstance(artigos, list)):
                #print('\nNão achei mais nada....')
                # ultima = encontra_elemento_visivel(driver, '#content > div > article > div > div > div.herald-ovrld > header > h1', By.CSS_SELECTOR)
                # if ultima.text == 'Página não encontrada!': break
                if limite_timeout > 10:
                    break
                else:
                    continue
        except:
            continue    

        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')

    return(lista_noticias)

def scrap_247_conteudo(lista_artigos):
    driver.set_page_load_timeout(15)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '/html/body/main/div[3]/div[1]/article', By.XPATH, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('div[3]/p')   
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:
                p_temp = p.get_attribute('innerHTML')  
                if 'http' in p_temp:
                    continue
                
                if p_temp[:13].find('247 -') != -1:
                    cortar = p_temp.find('</b>') + len('</b>')
                    p_temp = p_temp[cortar:]
                texto.append(p_temp) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass

    return lista_paginas

def scrap_republica(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []
    limite_timeout = 0
    n_pagina = 10 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}{n}'
            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '/html/body/div[1]/div[3]/div/div', By.XPATH)
            artigos = encontra_elemento_visivel(painel_artigos, '//article/div[2]/header/h3/a', By.XPATH)
            if not artigos or (not isinstance(artigos, list)):
                break
        except:
            continue    
        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
 
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    
    return(lista_noticias)

def scrap_republica_conteudo(lista_artigos):
    driver.set_page_load_timeout(15)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '/html/body/div[1]/div[3]/div/div/article/div[1]', By.XPATH, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('p')   
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:
                p_temp = p.get_attribute('innerHTML')  
                if 'http' in p_temp:
                    continue
 
                texto.append(p_temp) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass

    return lista_paginas

def scrap_senso(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []

    n_pagina = 10 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}{n}'
            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '/html/body/div[1]/div[6]/div[2]/div[9]/div[1]', By.XPATH)
            artigos = encontra_elemento_visivel(painel_artigos, 'div/div/a', By.XPATH)
            if not artigos or (not isinstance(artigos, list)):
                break
        except:
            continue    

        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
 
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    
    return(lista_noticias)

def scrap_senso_conteudo(lista_artigos):
    driver.set_page_load_timeout(15)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '/html/body/div[1]/div[6]/div[2]/div[2]/div/article', By.XPATH, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('div/p')   
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:
                p_temp = p.get_attribute('innerHTML')  
                if 'http' in p_temp:
                    continue
                if 'Seja membro' in p_temp:
                    break
                if 'Assine ' in p_temp:
                    break
                texto.append(p_temp) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass

    return lista_paginas

def scrap_dcm(url, url2, limite_artigos):
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')
        
    n_artigos = 0
    lista_noticias = []

    n_pagina = 20 #arigos por pagina
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}{n}/?s'
            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '/html/body/div[10]/div/div/div[1]/div', By.XPATH)
            
            artigos = encontra_elemento_visivel(painel_artigos, '//div/h3/a', By.XPATH)
            if not artigos or (not isinstance(artigos, list)):
                break
        except:
            continue    

        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
 
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    
    return(lista_noticias)

def scrap_dcm_conteudo(lista_artigos):
    driver.set_page_load_timeout(15)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, '/html/body/div[10]/article', By.XPATH, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('div[2]/p')  
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:
                p_temp = p.get_attribute('innerHTML')  
                if 'http' in p_temp:
                    continue
                if 'Seja membro' in p_temp:
                    break
                if 'Assine ' in p_temp:
                    break
                texto.append(p_temp) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            print('\nErro!')
            pass
    
    return lista_paginas


def scrap_g1(url, url2, limite_artigos):
    driver.set_page_load_timeout(10)
    driver.get(f'{url}')
    print(f'Conectando - {driver.title}')

    #Aguarda carregamento botão 'Carregar Mais'
    botao_carrega_mais = encontra_elemento_clicavel(driver, '#feed-placeholder > div > div > div.load-more.gui-color-primary-bg > a', By.CSS_SELECTOR)
    try: 

        prosseguir_lgpd = encontra_elemento_clicavel(driver, '#cookie-banner-lgpd > div > div.cookie-banner-lgpd_button-box > button', By.CSS_SELECTOR)
        prosseguir_lgpd.click()

        aguarda(INTERVALO)
    except:
        pass
        
    n_artigos = 0
    lista_noticias = []

    nova_pagina_tmp = f'{url2}-1.ghtml'
    driver.get(f'{nova_pagina_tmp}') 
    btn_notificacoes = encontra_elemento_clicavel(driver, '//*[@id="push-web-notification"]/div/div[2]/button[2]', By.XPATH, 10)
    driver.get(f'{nova_pagina_tmp}') 
    btn_notificacoes = encontra_elemento_clicavel(driver, '//*[@id="push-web-notification"]/div/div[2]/button[2]', By.XPATH, 10)
    if btn_notificacoes:
        btn_notificacoes.click()

    n_pagina = 10 #arigos por página
    for n in tqdm(range(1, limite_artigos//n_pagina + 1), total=limite_artigos//n_pagina, desc='Buscando mais artigos'):
        try:
            nova_pagina = f'{url2}-{n}.ghtml'

            driver.get(f'{nova_pagina}')
            painel_artigos = encontra_elemento_visivel(driver, '#feed-placeholder > div > div > div._l', By.CSS_SELECTOR)
            artigos = encontra_elemento_visivel(painel_artigos, 'a', By.TAG_NAME)
            if not artigos:
                continue
        except:
            print(f'\nTimeout em driver.get({nova_pagina})')
            
            input('\n[pause]')
            aguarda(1) 
        
            continue    
        for artigo in artigos:
            titulo = artigo.text
            link = artigo.get_attribute('href')
            if not link:
                continue
            if link.find('g1.globo.com') == -1:
                continue
            if link.find('/playlist/') != -1:
                continue
            try:
                if len(lista_noticias) > 0 and lista_noticias[-1]['link'] == link:
                    continue
                lista_noticias.append({
                    'pag'       : n, 
                    'site'      : url, 
                    'titulo'    : titulo,
                    'link'      : link
                })
            except:
                print('Ignorando parte do documento....')
                raise
            finally:
                n_artigos += 1    
 
    print(f'\nTotal de artigos a serem baixados: {len(lista_noticias)}')
    
    return(lista_noticias)

def scrap_g1_conteudo(lista_artigos):
    driver.set_page_load_timeout(10)
    lista_paginas = []
    for artigo in tqdm(lista_artigos, total=len(lista_artigos), desc='     Baixando artigos'):
        url = artigo['link']
        try:
            driver.get(f'{url}')                    
        except:
            print(f'\nTimeout em {url}')
            input('\n[pause]')
            continue    
        painel_paragrafos = encontra_elemento_visivel(driver, 'body > div.glb-grid > main > div.mc-article-body', By.CSS_SELECTOR, 3)
        try:
            if painel_paragrafos:
                paragrafos = painel_paragrafos.find_elements_by_xpath('article//p')   
            else:
                paragrafos = False
            if not paragrafos:
                continue
            texto = []
            for p in paragrafos:  
                texto.append(p.get_attribute('innerHTML')) 
        
            corpo = ' '.join(texto)
            lista_paginas.append({
                'site'      : url,         
                'titulo'    : artigo['titulo'],
                'corpo'     : remove_tags(corpo)            
            })
        except:
            pass  

    return lista_paginas

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--window-size=600,600")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    #chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(options=chrome_options, 
                            executable_path='C:\Program Files (x86)\chromedriver.exe')
    INTERVALO = 1 # em segundos
    aguarda(5)


#%% TERÇALIVRE
processa_site('tercalivre', 'noticias', 'brasil', 18000)
processa_site('tercalivre', 'noticias', 'mundo', 18000)
processa_site('tercalivre', 'noticias', 'politica', 18000)
lista_colunistas = scrap_tercalivre_colunistas('https://tercalivre.com.br/colunistas/')
for colunista in lista_colunistas:
   processa_site('tercalivre', 'colunista', colunista, 200000)

#%% 247
processa_site('247', 'noticias', 'poder', 27000)
processa_site('247', 'noticias', 'brasil', 27000)
processa_site('247', 'noticias', 'mundo', 27000)

#%% Conexão Política
processa_site('conexaopolitica', 'author', 'ailton', 300)
processa_site('conexaopolitica', 'author', 'alexcesar', 3500)
processa_site('conexaopolitica', 'author', 'bruno_lustosa', 3500)
processa_site('conexaopolitica', 'author', 'carlos_junior', 3500)
processa_site('conexaopolitica', 'author', 'eva', 3500)
processa_site('conexaopolitica', 'author', 'felipepedri', 3500)
processa_site('conexaopolitica', 'author', 'guilherme', 3500)
processa_site('conexaopolitica', 'author', 'leandroruschel', 3500)
processa_site('conexaopolitica', 'author', 'thaisgarcia', 3500)
processa_site('conexaopolitica', 'author', 'fahur', 3500)
processa_site('conexaopolitica', 'category', 'ultimas', 9000)
processa_site('conexaopolitica', 'category', 'brasil', 4500)
processa_site('conexaopolitica', 'category', 'mundo', 3500)

#%% República de Curitiba
processa_site('republica', '', '', 7500)

#%% Senso Incomum
processa_site('senso', 'drops', '', 1760)
processa_site('senso', 'artigos', '', 1050)

#%%DCM
processa_site('dcm', 'artigos', '', 124000)









