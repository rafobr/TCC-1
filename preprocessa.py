import json 
import nltk    
from nltk import tokenize
from nltk.corpus import stopwords  
from nltk.tokenize import word_tokenize  
import re  
import os

def remove_stopwords(lista):
    '''Remove stopwords de uma lista'''
    lista_minima = [w for w in lista if len(w) > 1]
    stop_words = set(stopwords.words('portuguese')) 
    minhas_stop_words = ['...', '....', '\'\'', '``', 'nbsp', '\'', 
                        'segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira',
                        'disse', 'diz', 'dizer', 'falou', 'fala','falar', 'afirmou', 'afirma', 'afirmar',
                        'faz', 'fez', 'alguma', 'desse', 'dessa', 'disso', 'disto', 'tem', 'têm',
                        'hoje', 'amanhã', 'ontem', 'agora', 'depois', 'antes', 'segundo', 'após',
                        'além', 'assim', 'sobre', 'então', 'desde', 'pois', 'entanto', 'onde', 
                        'fazer', 'qualquer', 'nesta', 'ainda', 'vai', 'vão', 'ter', 'se', 'porque', 'aí', 'daí'
                        'anos', 'meses', 'apenas', 'atrás', '--', 'dde', 'the', 'http', 'https']
    lista_filtrada = [w for w in lista_minima if not w in stop_words]  
    minha_lista_filtrada = [w for w in lista_filtrada if not w in minhas_stop_words]  
    return minha_lista_filtrada

def remove_tags_amazon(texto):
    '''Remove marcações/tags HTML de um texto'''
    import re
    limpo = re.compile('\[amazon.*\]')
    sem_tags = re.sub(limpo, '', texto)
    return sem_tags

def remove_nome_portais(texto):
    '''Remove referência a portais/sites de um texto'''
    import re

    portais = ['terça livre', ' 247', ' dcm', 'republica de curitiba', 'senso incomum', 'conexão política']
    
    texto_novo = texto
    for portal in portais:
        limpo = re.compile('.*' + portal + '.*')
        texto_novo = re.sub(limpo, '', texto_novo)
    return texto_novo

def remove_erros(lista_tokens):
    '''Substitui erros de ortografia e pontuação de um texto'''
     
    erros = ['\'', '-', '.'] 
    for i, token in enumerate(lista_tokens):
        if token in ['boslonaro', 'bolsoanro', 'bolosonaro', 'bolsonado',  'bolsoanaro', 'bolosnaro', 'bolsnaro', 'bolsonro', 'bolsobaro', 'bosonaro',  'bolsonar', 'bolsonaor']:
            lista_tokens[i] = 'bolsonaro'
        elif token in ['diereita']:
            lista_tokens[i] = 'direita'            
        elif token in ['dallgnol', 'dallangol', 'dallganol', 'dellagnol', 'dellagnoll', 'dallangnol']:
            lista_tokens[i] = 'dallagnol'            
        elif token in ['doria']:
            lista_tokens[i] = 'dória'            
        elif token in ['psbd']:
            lista_tokens[i] = 'psdb'            
        elif token in ['amoedo', 'amôedo']:
            lista_tokens[i] = 'amoêdo'        
        elif token in ['gudes']:
            lista_tokens[i] = 'guedes'        
        elif token in ['rouseff', 'roussef']:
            lista_tokens[i] = 'rousseff'        
        elif token in ['onix', 'onyz']:
            lista_tokens[i] = 'onyx'         
        elif token in ['tump', 'trum']:
            lista_tokens[i] = 'trump'            
        elif token in ['intecept', 'inthercept', 'intercpet', 'intercep']:
            lista_tokens[i] = 'intercept'            
        elif 'twitter.com' in token :
            lista_tokens[i] = 'twitter'            
        elif '.com' in token :
            lista_tokens[i] = 'site'            
        if token[0] in erros:
            lista_tokens[i] = token[1:]
        if token[-1] in erros:
            lista_tokens[i] = token[:-1]   
    return lista_tokens  


def aplica_stemmer(lista_palavras):
    '''Aplica stemmer em uma lista de palavras'''
    lista_palavras_stemmed = []
    stemmer = nltk.stem.RSLPStemmer()
    for palavra in lista_palavras:
        lista_palavras_stemmed.append(stemmer.stem(palavra))
        
    return lista_palavras_stemmed

def recupera_arquivos_data():
    '''Importa arquivos de dados para processamento'''
    files = [f for f in os.listdir('data/dataset_final') if os.path.isfile('data/dataset_final/' + f) and f[-5:] == '.json' and f[:2] != 't-' and f[-10:-5] != 'sites']
    return files


if __name__ == '__main__':
    lista_arquivos_entrada = recupera_arquivos_data()
    for nome_arquivo in lista_arquivos_entrada:
        caminho = 'data/dataset_final/'
        print(f'Processando arquivo {nome_arquivo} ...')
        
        with open(caminho + nome_arquivo, 'r', encoding = 'utf-8') as arquivo_json:
            dados = json.load(arquivo_json)

        palavras = []
        for artigo in dados:
            texto = ""
            for item in artigo:
                if item in ['titulo', 'corpo']:
                    texto += f' {artigo[item]}'.lower() 

            texto_sem_tags = remove_tags_amazon(texto)
            texto_final = remove_nome_portais(texto_sem_tags)
            if len(texto) == 0:
                continue
            palavras_tokenize = tokenize.word_tokenize(texto_final, language='portuguese')   
            tokens_final = remove_erros(remove_stopwords(palavras_tokenize))
            
            if len(tokens_final) > 2:
                palavras.append(tokens_final)

        if palavras:
            with open(caminho + 't-' + nome_arquivo, 'w', encoding = 'utf-8') as arquivo_token:
                json.dump(palavras, arquivo_token, ensure_ascii=False)
            
