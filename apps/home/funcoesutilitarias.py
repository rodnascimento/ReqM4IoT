from .models import *
from django.contrib.auth.models import User
import json
from django.shortcuts import get_object_or_404
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
import re
def criar_projeto(dados_projeto, id_usuario):
    '''
    dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'modelagens': {0:{'nome':'nome', 'ling_model': 'ling_model', 'tipo': 'tipo', 'dados':'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel>'}},
        'requisitos_iot': {"Contextualizados":[], "SensoresIncompletos":[],"AtuadoresIncompletos":[]},
        'modelo_dict': {
            'centroids': "modelo_carregado.cluster_centers_.tolist()",
            'labels': "modelo_carregado.labels_.tolist()"
        }
    }
    dados_projeto = {'nome': 'Nome', 'dados' = None}
    '''
    dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'modelagens': {},
        'requisitos_iot': {"Contextualizados":[], "SensoresIncompletos":[],"AtuadoresIncompletos":[]},
        'classificador': {
            'centroids': False,
            'labels': False
            }
    }
    try:
        projeto = Projetos(dados=json.dumps(dados), nome_projeto=dados_projeto['nome'],descricao=dados_projeto['descricao'], id_criador=id_usuario)
        projeto.save()
        try: 
            usuario = get_object_or_404(User, pk=id_usuario)
            projeto_usuario = ProjetosUsuarios(user=usuario, projeto=projeto)
            projeto_usuario.save()
        except Exception as e:
            print(f"Erro ao deletar projeto: {e}")
        return True
    except Exception as e:
        print(f"Erro ao criar projeto: {e}")
        return False
def atualizar_projeto(dados_projeto_original, dados_projeto_novos):
    resultado = Projetos.objects.filter(nome_projeto=dados_projeto_original['nome']).first()
    if resultado:
        resultado.nome_projeto = dados_projeto_novos['nome']
        resultado.dados = dados_projeto_novos['dados']
        resultado.save()
        return True
    return False

def filtrar_projetos_usuario(usuario):
    
    projetos = ProjetosUsuarios.objects.filter(user=usuario.id)
    return projetos

def formatar_projetos_usuario(projetos,usuario):
    retorno = []
    for projeto in projetos:
        dados = {}
        id_projeto = projeto.projeto.id
        dados_projeto = get_object_or_404(Projetos, id=id_projeto)
        dados['id'] = id_projeto
        dados['nome']= dados_projeto.nome_projeto
        dados['descricao']= dados_projeto.descricao
        dados['criacao'] = dados_projeto.criacao.strftime("%d/%m/%Y")
        dados['criador'] = get_object_or_404(User, id=dados_projeto.id_criador).username
        dados['e_o_criador'] = usuario.id==dados_projeto.id_criador
        retorno.append(dados)
    return retorno

class AnaliseSintatica:
    def __init__(self, requisitos, tagger,passive_voice):
        self.tagger=tagger
        self.chunker=nltk.RegexpParser("""
                      AdvP: {<QL>?<AB.*>?<RB.*>+}                         #Para extrair Adverbial Phrases
                      AP: {<AB.*>?<AdvP>?<QL>?<JJ.*>+}                    #Para extrair Adjective Phrases
                      NP: {<PP.*>?<CS>?<DT>?<AT>?<AP>?<NN.*>+|<PPS.*>}    #Para extrair Noun Phrases
                      P: {<IN.*>|<TO>}                                    #Para extrair preposições
                      PP: {<P>+<NP>?}                                     #Para extrair Preposition Phrases
                      MOD: {<MD>}                                         #Para extrair Modal Auxiliare
                      V: {<VB.*>|<BE.*>|<DO.*>|<HV.*>}                    #Para extrair os verbos
                      VP: {<MOD>?<V>+<NP>*<PP>*<AP>*<AdvP>*}              #Para extrair Verb Phrases
                      CCPP: {<P><CC><P>}                                  #Para extrair Coordination Preposition Phases
                      CCNP: {<NP><CC><NP>}                                #Para extrair Coordination Noun Phrases
                      CCAP: {<AP><CC><AP>}                                #Para extrair Coordination Adjective Phrases
                      """)
        self.passive_voice=passive_voice
        self.analise_sintatica={'PV': [],'MS':[],'MVM': [],'DS':[]}
        self.requisitos=requisitos
    
    def obter_nos(self,arvore):
        largura=len(arvore)
        nodes=[]
        for i in range(largura):
            if type(arvore[i]) is nltk.Tree:
                nodes.append(arvore[i].label())
            else:
                nodes.append(arvore[i][1])
        return nodes
    
    def sequencia_tags(self,tags):
        retorno = ""
        for tag in tags:
            retorno+=tag[1]
        return retorno
    
    def voz_passiva(self,tags,passivevoice):
        for padrao in passivevoice:
            if padrao in tags:
                return True
        return False
    def obter_sujeito(self,arvore):
        largura=len(arvore)
        for i in range(largura):
            if type(arvore[i]) is nltk.Tree:
                if(arvore[i].label()=='NP'):
                    retorno=[]
                    for word in arvore[i]:
                        retorno.append(word[0])
                    return ' '.join(retorno)
            else:
                if(arvore[i][1]=='NP'):
                    return(arvore[i][0])
    
    def arvore_sintatica(self,sentences,passivevoice):
        for sentence in sentences:
            if len(sentence)==0:
                return "OK"
            tagged_sentence = self.tagger.tag(nltk.word_tokenize(sentence))
            sintaxe_tree = self.chunker.parse(tagged_sentence)
            nodes = self.obter_nos(sintaxe_tree)
            if not ('VP' or 'V' or 'MOD') in nodes:
                return("MVM")
            sequencia = self.sequencia_tags(sintaxe_tree.leaves())
            if(self.voz_passiva(sequencia,passivevoice)):
                return("PV")
            if not ('NP' in nodes[0:nodes.index('VP')] or 'CCNP' in nodes[0:nodes.index('VP')]):
                return("MS")
            else:
                subject = self.obter_sujeito(sintaxe_tree).lower()
                if ('it' in subject or 'there' in subject):
                    return("DS")
            return "OK"
    def analise_completa(self):
        for indice,req in enumerate(self.requisitos):
            req=re.sub("[! - &;™,]+",' ',req)
            sentences = req.split('.')
            erro = self.arvore_sintatica(sentences,self.passive_voice)
            if erro!="OK":
                self.analise_sintatica[erro].append(indice)

    def analise(self):
        self.analise_completa()
        return self.analise_sintatica

class ambiguidade_lexica:
    def __init__(self, requisitos, palavras_amb,POS):
        self.requisitos=requisitos
        self.ambiguos_lexicos = {"PA": [], "AFL": []}
        self.palavras_amb=palavras_amb
        self.POS=POS
        self.tokens=[]
    
    def palavras_ambiguas(self):
        for indice,req in enumerate(self.requisitos):
            self.tokens.append(nltk.word_tokenize(req))
            for ambigua in self.palavras_amb:
                if ambigua.lower() in self.tokens[indice]:
                    self.ambiguos_lexicos["PA"].append(indice)

    def objetoWN(self,pos):
        
        if pos == 'V':
            return nltk.corpus.wordnet.VERB
        elif pos == 'N':
            return nltk.corpus.wordnet.NOUN
        elif pos == 'R':
            return nltk.corpus.wordnet.ADV
        elif pos == 'J':
            return nltk.corpus.wordnet.ADJ
        else:
            return nltk.corpus.wordnet.NOUN
    
    def algoritmo_flex_amb(self):
        LIMIAR_MIN = 3 / 4
        QTDE_SIM = 3
        tokens_limpos=[nltk.word_tokenize(req) for req in limpeza(self.requisitos)[1]]

        for indice,req in enumerate(self.POS):
            qtde = len(tokens_limpos[indice])
            possiveis = []
            for token in req:
                if len(nltk.corpus.wordnet.synsets(token[0], pos=self.objetoWN(token[1][0]))) > QTDE_SIM:
                    possiveis.append(req[0])
            if len(possiveis) >= (LIMIAR_MIN * qtde):
                self.ambiguos_lexicos["AFL"].append(indice)
    
    def requisitos_ambiguos(self):
        self.palavras_ambiguas()
        self.algoritmo_flex_amb()
        return self.ambiguos_lexicos


class ambiguidade_sintatica:
    def __init__(self, requisitos, POS):
        self.requisitos=requisitos
        self.POS=POS
        self.ambiguidade=[]
    def texto(self, tags):
        retorno = []
        for tag in tags:
            retorno.append(tag[0])
        return ' '.join(retorno)
    def obter_ambiguidade(self, tree,tipo):
        largura=len(tree)
        ocorrencia=[]
        for i in range(largura):
            if (type(tree[i]) is nltk.Tree) and (tree[i].label()==tipo):
                nos=[]
                for k in range(len(tree[i])):
                    if (type(tree[i][k]) is nltk.Tree): 

                        nos.append((tree[i][k].label(),self.texto(tree[i][k].leaves())))
                ocorrencia.append((self.texto(tree[i].leaves()),nos))
        return ocorrencia
    
    def analitical_ambiguity(self,pos):
        Analitical = nltk.RegexpParser("""
                                AP: {<AB.*>?<AdvP>?<QL>?<JJ.*>?}              #Para extrair Adjective Phrases
                                NP: {<PP.*>?<CS>?<DT>?<AT>?<NN.*>|<PPS.*>|<NP>}    #Para extrair Noun Phrases
                                Analitical: {<AP><NP><NP>}                    #Definição de Analitical Ambiguity
                                """)
        sintaxe_tree = Analitical.parse(pos)
        ambiguidades = self.obter_ambiguidade(sintaxe_tree,"Analitical")
        retorno=[]
        if len(ambiguidades)==0:
            return False,retorno
        else:
            
            for ambiguo in ambiguidades:

                solucao_1 = f'{ambiguo[1][2][1]} of {ambiguo[1][0][1]} {ambiguo[1][1][1]}'
                solucao_2 = f'{ambiguo[1][0][1]} {ambiguo[1][2][1]} of {ambiguo[1][1][1]}'

                texto_retorno = f"O texto '{ambiguo[0]}' tem Analitical Ambiguity e tem as possíveis leituras '{solucao_1}' e '{solucao_2}'."
                retorno.append(texto_retorno)
            return True,retorno
    def coordination_ambiguity(self, pos):
        Coordination = nltk.RegexpParser("""
                            AP: {<AB.*>?<QL>?<JJ.*>?}                     #Para extrair Adjective
                            NP: {<PP.*>?<CS>?<DT>?<AT>?<NN.*>|<PPS.*>|<NP>}    #Para extrair Noun Phrases
                            Coordination: {<AP><NP><CC><NP>}              #Definição de Coordination Ambiguity
                            """)

        sintaxe_tree = Coordination.parse(pos)
        ambiguidades = self.obter_ambiguidade(sintaxe_tree,"Coordination")
        retorno=[]
        if len(ambiguidades)==0:
            return False, retorno
        else:
            
            for ambiguo in ambiguidades:
                solucao = f'{ambiguo[1][0][1]} {ambiguo[1][1][1]}, {ambiguo[1][0][1]} {ambiguo[1][2][1]}'

                texto_retorno=f"O texto '{ambiguo[0]}' pode ser lido da maneira que está, ou da seguinte forma: {solucao}"
                retorno.append(texto_retorno)
            return True, retorno
    
    def attachment_ambiguity(self, pos):
        Attachment = nltk.RegexpParser("""
                            NP: {<PP.*>?<CS>?<DT>?<AT>?<AP>?<NN.*>|<PPS.*>|<NP>}    #Para extrair Noun Phrases
                            P: {<IN.*>|<TO>}                                   #Para extrair preposições
                            V: {<VB.*>|<DO.*>|<HV.*>}                          #Para extrair os verbos
                            Attachment: {<V><NP><P><NP>}                       #Definição de Attachment Ambiguity
                            """)
        sintaxe_tree = Attachment.parse(pos)
        ambiguidades = self.obter_ambiguidade(sintaxe_tree,"Attachment")
        retorno=[]
        if len(ambiguidades)==0:
            return False,retorno
        else:

            for ambiguo in ambiguidades:
                consulta_1 = ambiguo[1][1][1]+' '+ambiguo[1][2][1]+' '+ambiguo[1][3][1]
                consulta_2 = ambiguo[1][0][1]+' '+ambiguo[1][2][1]+' '+ambiguo[1][3][1]
                consultas=[consulta_1,consulta_2]
                solucao_1 = consulta_1
                solucao_2 = consulta_2
                texto_retorno=f"O texto '{ambiguo[0]}' tem Coordination Ambiguity, tem as duas leituras possíveis: '{solucao_1}' e '{solucao_2}'."
                retorno.append(texto_retorno)
            return True, retorno
    
    def retorna_ambiguidade(self):
        retorno={'Analitical':{},'Coordination':{},'Attachment':{}}
        for indice,requisito in enumerate(self.POS):
            if(self.analitical_ambiguity(requisito)[0]):
                retorno['Analitical'][indice]= self.analitical_ambiguity(requisito)[1]
            if(self.coordination_ambiguity(requisito)[0]):
                retorno['Coordination'][indice]= self.coordination_ambiguity(requisito)[1]
            if(self.attachment_ambiguity(requisito)[0]):
                retorno['Attachment'][indice]= self.attachment_ambiguity(requisito)[1]
        return retorno

class Contextualizacao:
    def __init__(self, requisitos,nome_arquivo_ontologia,pesos={'centroids': False,'labels': False}):
        self.requisitos=requisitos
        self.arquivo=nome_arquivo_ontologia
        self.dicionario_palavras_smart={}
        self.contextualizados = {"Contextualizados":[], "SensoresIncompletos":[],"AtuadoresIncompletos":[]}
        self.sensores=[]
        self.peso=pesos
    def tratamento_ontologia(self):
        arquivo = open(self.arquivo,'r')
        arq = ''
        for i in arquivo:
            arq+=i
        arquivo.close()
        palavras_smart=arq.split('\n')

        for palavra in palavras_smart:
            chave,valor=palavra.split(',')
            self.dicionario_palavras_smart[chave]=int(valor)
    def sensores(self):
        arquivo = open("apps/static/assets/arquivos_requisitos/sensores.txt",'r')
        arq = ''
        for i in arquivo:
            arq+=i
        arquivo.close()
        self.sensores=arq.split('\n')
    def OR(self,array1,array2):
        aux=[]
        for i in range(len(array1)):
            aux.append(array1[i] or array2[i])
        return aux 

    def contextualizacao(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        import pandas as pd
        import numpy as np
        from sklearn.cluster import KMeans
        requisitos=limpeza(self.requisitos)[1]
        self.tratamento_ontologia()
        tfidfvectorizer = TfidfVectorizer(analyzer='word', stop_words='english')

        tfidf_wm = tfidfvectorizer.fit_transform(requisitos)
        palavras = list(tfidfvectorizer.get_feature_names_out())
        df_tfidfvect = pd.DataFrame(data=tfidf_wm.toarray(), columns=palavras)
        palavras_smart=list(self.dicionario_palavras_smart.keys())
        df = df_tfidfvect
        #if self.peso["centroids"]==False:
        n = 2
        kmeans = KMeans(n_clusters=n, random_state=0,n_init=10)
        kmeans.fit(df)
        labels = kmeans.labels_
        self.peso['centroids'] = kmeans.cluster_centers_.tolist()
        self.peso['labels'] = kmeans.labels_.tolist()
        classe_0 = [not bool(x) for x in labels]
        classe_1 = [bool(x) for x in labels]
        classe_0 = df[classe_0]
        classe_1 = df[classe_1]


        
        
        indices_0 = list(classe_0.mean() == 0)
        indices_0 = list(classe_0.mean()[indices_0].index)
        indices_1 = list(classe_1.mean() == 0)
        indices_1 = list(classe_1.mean()[indices_1].index)

        classe_1 = classe_1.drop(columns=indices_1)
        classe_0 = classe_0.drop(columns=indices_0)

        palavras_0 = list(classe_0.columns)
        palavras_1 = list(classe_1.columns)
        
        palavras_check_0 = []
        for i in range(len(palavras_0)):
            for palavra in palavras_smart:
                if palavras_0[i] in palavra:
                    if palavras_0[i] not in palavras_check_0:
                        palavras_check_0.append(palavras_0[i])
        palavras_check_1 = []
        for i in range(len(palavras_1)):
            for palavra in palavras_smart:
                if palavras_1[i] in palavra:
                    if palavras_1[i] not in palavras_check_1:
                        palavras_check_1.append(palavras_1[i])

        media_0 = classe_0.mean()[palavras_check_0]
        media_1 = classe_1.mean()[palavras_check_1]
    
        score_0 = media_0.sum()
        score_1 = media_1.sum()

        
        if score_0 > score_1:
            classe=0
            qtde_palavras=len(palavras_0)
        else:
            classe=1
            qtde_palavras = len(palavras_1)

        if classe==1:
            pass
        else:
            aux=[]
            '''print('labels sem mexer: ',list(labels))'''
            for i in list(labels):
                if i==0:
                    i=1
                elif i==1:
                    i=0
                aux.append(i)
            labels=aux
        
        vetor=[0 for i in range(len(palavras))]
        for chave,valor in self.dicionario_palavras_smart.items():
            if len(chave.split(' '))==1:
                if chave in palavras:
                    indice=palavras.index(chave)
                    vetor[indice]=valor
            else:
                aux=0
                for mini_chave in chave.split(' '):
                    if mini_chave in palavras:
                        aux+=1
                if aux==len(chave.split(' ')):
                    for mini_chave in chave.split(' '):
                        indice=palavras.index(mini_chave)
                        vetor[indice]=valor
        df_pesos=pd.DataFrame(vetor,index=palavras)
        vetor_pesos=np.array(vetor)

        array_score=[]
        for indice in range(len(self.requisitos)):
            linha=df_tfidfvect.iloc[indice]
            array_linha=np.array(linha)
            array_score.append(np.dot(vetor_pesos,array_linha))
        media_score=sum(array_score)/len(array_score)

        resultado=[]
        for i in array_score:
            if i>=media_score:
                resultado.append(1)
            else:
                resultado.append(0)
        
        array_or=self.OR(labels,resultado)
        self.contextualizados["Contextualizados"]=[indice for indice,valor in enumerate(array_or) if valor==1]
    
    def completude(self):
        tokens, requisitos=limpeza(self.requisitos)
        pos = trigram_pos(requisitos)
        
        
        for indice in self.contextualizados["Contextualizados"]:
            palavras=tokens[indice]
            
            for i,palavra in enumerate(palavras):
                # 1 - Sensor sem definição do sensor
                if(palavra=="sensor" or palavra=="sensors"):
                    if not ((palavras[i - 1] in self.sensores)):
                        if indice not in self.contextualizados["SensoresIncompletos"]:
                            self.contextualizados["SensoresIncompletos"].append(indice)

                        
                        
                # 2 - Atuadores sem definição
                if (palavra == "actuator" or palavra == "actuators"):
                    try:
                        if not ((pos[indice][i+1][1]=='RB') or (pos[indice][i+1][1][0]=='V')):
                            if indice not in self.contextualizados["AtuadoresIncompletos"]:
                                self.contextualizados["AtuadoresIncompletos"].append(indice)
                    except:
                        if indice not in self.contextualizados["AtuadoresIncompletos"]:
                            self.contextualizados["AtuadoresIncompletos"].append(indice)
    
    def analise_contextualizacao(self):
        self.contextualizacao()
        self.completude()
        return self.contextualizados,self.peso


def limpeza(requisitos):
    tokens = []
    import copy
    interno = copy.deepcopy(requisitos)
    for indice,req in enumerate(interno):
        req= re.sub("[!'@*>=+#%:&;™.,_\\/()?\"]+", ' ', req)
        req= re.sub('[0-9]+', ' ', req)
        req= re.sub('- | -|-+', ' ', req)
        req= re.sub(r'(?:^| \\ )\w(?:$| )', ' ', req).strip()
        words = nltk.word_tokenize(req.lower())
        words = words[1:]
        tokens.append(words)
        newwords = []
        for word in words:
            if word in nltk.corpus.stopwords.words('english'):
                continue
            try:
                newwords.append(word)
            except:
                continue
        interno[indice] = ' '.join(newwords)
    return tokens,interno

def trigram_pos(requisitos):
    from pickle import load
    entrada = open('apps/static/assets/arquivos_requisitos/trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    saida=[tagger.tag(nltk.word_tokenize(requisito)) for requisito in requisitos]

    return saida

def caminho(escolha, requisitos):
    print(requisitos)
    from pickle import load
    #entrada = open('/static/assets/arquivos_requisitos/trigram.pkl','rb')
    entrada = open('apps/static/assets/arquivos_requisitos/trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    aux=[]
    for requisito in requisitos.values():
        aux.append(requisito[0])
    requisitos=aux

    if escolha == 1:
        arquivo = open('apps/static/assets/arquivos_requisitos/passivevoice.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        passive_voice = texto.split('\n')
        analise_sintatica = AnaliseSintatica(requisitos,tagger,passive_voice).analise()
        PV = analise_sintatica['PV']
        MS = analise_sintatica['MS']
        MVM = analise_sintatica['MVM']
        DS = analise_sintatica['DS']
        
        headings = ("Ausência de Verbos", "Voz Passiva", "Falta de Sujeito", "Dummy Subject")
        Data = []
        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in MVM)
            aux.append(indice in PV)
            aux.append(indice in MS)
            aux.append(indice in DS)

            Data.append((requisitos[indice], aux))
    elif escolha ==2:
        arquivo = open('apps/static/assets/arquivos_requisitos/dicionario_base.txt','r')
        texto = ''
        for linhas in arquivo:
            texto+=linhas
        arquivo.close()
        palavra_amb = texto.split('\n')
        pos = trigram_pos(limpeza(requisitos)[1])
        amb_lexical = ambiguidade_lexica(requisitos,palavra_amb,pos).requisitos_ambiguos()
        amb_sintatica = ambiguidade_sintatica(requisitos,pos).retorna_ambiguidade()
        PA = amb_lexical['PA']
        AFL = amb_lexical['AFL']
        Analitical = list(amb_sintatica['Analitical'].keys())
        Coordination = list(amb_sintatica['Coordination'].keys())
        Attachment = list(amb_sintatica['Attachment'].keys())
        
        headings = ("Palavra Ambigua", "Algoritmo Flexible Ambiguity", "Ambiguidade Analitica", "Ambiguidade por Coordenação", "Ambiguidade de ligação")
        Data = []
        for indice in range(len(requisitos)):
            aux = []
            aux.append(indice in PA)
            aux.append(indice in AFL)
            aux.append(indice in Analitical)
            aux.append(indice in Coordination)
            aux.append(indice in Attachment)
            Data.append((requisitos[indice], aux))
    
    elif escolha ==3:
        headings = ("Nº Requisito", "Contextualizados", "Completos")
        contextualizados,pesos = Contextualizacao(requisitos,"apps/static/assets/arquivos_requisitos/m3-ontology.txt").analise_contextualizacao()
        Contex = contextualizados['Contextualizados']
        Sensores = contextualizados['SensoresIncompletos']
        Atuadores = contextualizados["AtuadoresIncompletos"]
        Data = []
        for i in range(len(requisitos)):
            aux = []
            aux.append(i in Contex)
            aux.append(i in Sensores)
            aux.append(i in Atuadores)
            if True in aux:
                Data.append((requisitos[i], aux))
            else:
                continue
            return contextualizados, Data,pesos

    return [Data, headings, requisitos]

def obter_requisitos(projeto):
    dados = json.loads(projeto.dados)
    requisitos={}
    funcionais = dados["requisitos_funcionais"]
    requisitos = {i:[requisito, 'Functional'] for i,requisito in enumerate(funcionais)}

    classes = dados["requisitos_nao_funcionais"].keys()
    indice=len(funcionais)
    for classe in classes:
        for requisito in dados["requisitos_nao_funcionais"][classe]:
            requisitos[indice]=[requisito, classe]
            indice=indice+1
    return requisitos

def tratar_requisitos(f):
    if f.name.split('.')[1]=='txt':
        mensagem = ""
        mensagem = f.read().decode('utf-8').split('\n')
        return mensagem
    elif f.name.split('.')[1]=='docx':
        import docx2txt as converte
        txt = converte.process(f.read())
        return txt.split('\n\n')

