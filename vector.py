from gensim.models import Word2Vec
import json
import os
from datetime import datetime

def recupera_arquivos_token(filtro=None):
    ''' Carrega dados de arquivos json com tokens '''
    files = [f for f in os.listdir('data/dataset_final') if os.path.isfile('data/dataset_final/' + f) and f[-5:] == '.json' and f[:2] == 't-']
    print(f'filtro={filtro}')
    if filtro == 'E':
        return filter(lambda p: ('247' in p) or ('dcm' in p), files)
    elif filtro == 'D':
        return filter(lambda p: ('conexaopolitica' in p) or ('republica' in p)  or ('senso' in p) or ('tercalivre') in p, files)
    elif filtro == 'ED' or filtro == 'DE':
        return filter(lambda p: 'g1' not in p, files)
    elif filtro == 'I' or filtro == 'DE':
        return filter(lambda p: 'g1' in p, files)      
    elif filtro:
        return filter(lambda p: filtro in p, files)                
    else:
        return files

if __name__ == '__main__':  
    lista_arquivos_entrada = recupera_arquivos_token(filtro='ED') 
    print(lista_arquivos_entrada)
    dados = []

    for nome_arquivo in lista_arquivos_entrada:
        caminho = 'data/dataset_final/'
        print(f'\nCarregando {nome_arquivo}...')
        with open(caminho + nome_arquivo, 'r', encoding = 'utf-8') as arquivo_json:
            artigos = json.load(arquivo_json)
            print(f'{len(artigos)} artigos carregados ')
            dados.extend(artigos)
           
    print(f'\n{len(dados)} artigos no TOTAL')

    #%%
    hora = datetime.now().strftime("%H:%M:%S")
    print(f'\n({hora}) Gerando modelo para word vectors...')
    modelo = Word2Vec(dados, min_count=1, size=300, workers=3, window=5, sg = 1)
    hora = datetime.now().strftime("%H:%M:%S")
    print(f'({hora}) Modelo gerado...')
    
    words = list(modelo.wv.vocab)
    hora = datetime.now().strftime("%H:%M:%S")
    print(f'\n({hora}) Salvando modelo...')
    word_vectors = modelo.wv
    word_vectors.save("artigos.wv")
