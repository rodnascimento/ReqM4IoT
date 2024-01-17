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
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': Texto, 'imagem': 'texto'}],
        'sequencia': [{'nome': Texto, 'imagem': 'texto'}],
        'requisitos_iot': {}
    }
    dados_projeto = {'nome': 'Nome', 'dados' = None}
    '''
    dados = {
        'requisitos_funcionais': [],
        'requisitos_nao_funcionais': {},
        'casos_de_uso': [],
        'maquina_de_estados': [{'nome': 'Texto', 'imagem': 'texto'}],
        'sequencia': [{'nome': 'Texto', 'imagem': 'texto'}],
        'requisitos_iot': {}
    }
    try:
        projeto = Projetos(dados=json.dumps(dados), nome_projeto=dados_projeto['nome'], id_criador=id_usuario)
        projeto.save()
        try: 
            usuario = get_object_or_404(User, pk=id_usuario)
            projeto_usuario = ProjetosUsuarios(user=usuario, projeto=projeto)
            projeto_usuario.save()
        except Exception as e:
            # Trate o erro de maneira mais específica (ex: log, mensagem)
            print(f"Erro ao deletar projeto: {e}")

        return True
    except Exception as e:
        # Trate o erro de maneira mais específica (ex: log, mensagem)
        print(f"Erro ao criar projeto: {e}")
        return False
'''
def deletar_projeto(pk):
    try:
        projeto = get_object_or_404(Projetos, pk=pk)
        projeto.delete()
        return True
    except Exception as e:
        # Trate o erro de maneira mais específica (ex: log, mensagem)
        print(f"Erro ao deletar projeto: {e}")
        return False
'''
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
            req = req.split(':')[1]
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
    entrada = open('/home/brunocarvalho/ReqM4IoT/ReqM4IoT/apps/static/assets/arquivos_requisitos/trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    saida=[tagger.tag(nltk.word_tokenize(requisito)) for requisito in requisitos]

    return saida

def caminho(escolha, requisitos):
    from pickle import load
    entrada = open('/home/brunocarvalho/ReqM4IoT/ReqM4IoT/apps/static/assets/arquivos_requisitos/trigram.pkl','rb')
    tagger = load(entrada)
    entrada.close()
    
    if escolha == 1:
        arquivo = open('/home/brunocarvalho/ReqM4IoT/ReqM4IoT/apps/static/assets/arquivos_requisitos/passivevoice.txt','r')
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
        arquivo = open('/home/brunocarvalho/ReqM4IoT/ReqM4IoT/apps/static/assets/arquivos_requisitos/dicionario_base.txt','r')
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
    return [Data, headings, requisitos]

def obter_requisitos(projeto):
    dados = json.loads(projeto.dados)
    requisitos = dados["requisitos_funcionais"]
    requisitos = {i:requisito for i,requisito in enumerate(requisitos)}
    return requisitos
