import json, requests
import pandas as pd
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

# ============ CARREGAR DADOS ============
historico_duvidas = pd.read_csv("./data/historico_duvidas.csv", encoding="utf-8")
perfil_do_desenvolvedor = json.load(open("./data/perfil_dev.json", encoding="utf-8"))
erros_comuns = pd.read_csv("./data/erros_comuns.csv", encoding="utf-8")

# ============ MONTAR CONTEXTO ============
contexto = """
PERFIL DO DESENVOLVEDOR (data/perfil_dev.json):
{
    "nome": "Victor",
    "idade": 22,
    "profissao": "Estudante de Python",
    "nivel_conhecimento": "Iniciante em Python",
    "objetivo": "Ter a mentalidade de um desenvolvedor podendo aplicar seus estudos da melhor forma no mercado de trabalho sempre encontrando soluções ótimas para o problema que enfrentar",   
    "perfil_aprendizado": "Gosta de ser perguntado até entender a resolução de sua dúvida e gosta de respostas completas repleta de conteúdo"
}

HISTORICO DE DUVIDAS (data/historico_duvidas.csv):
data,topico,conceito,duvida,resolvido,nivel_dificuldade,precisou_resposta_direta
2025-01-10,variaveis,variaveis,"Nao entendi como funcionam as variaveis",sim,1,sim
2025-01-15,variaveis,tipos_primitivos,"Qual a diferenca entre int e float?",sim,1,nao
2025-01-20,entrada_saida,input,"Como ausar input para receber dados?",sim,1,sim
2025-01-25,condicionais,if_else,"Nao entendi quando usar else",sim,1,nao
2025-02-01,condicionais,elif,"Qual a diferenca entre elif e varios ifs?",sim,2,sim
2025-02-05,loops,for,"Nao entendi como funciona o for",sim,2,sim
2025-02-10,loops,while,"Meu while entra em loop infinito",sim,2,sim
2025-02-15,loops,range,"Nao entendi o uso da funcao range",sim,1,nao
2025-02-20,listas,indices,"Recebi IndexError ao acessar lista",sim,2,nao
2025-02-25,listas,append,"Como adicionar elementos em uma lista?",sim,1,nao
2025-03-01,listas,percorrer_lista,"Qual a melhor forma de percorrer uma lista?",sim,2,sim
2025-03-05,tuplas,tuplas,"Nao entendi a diferenca entre lista e tupla",sim,2,sim
2025-03-10,dicionarios,chaves,"Recebi KeyError ao acessar uma chave",sim,2,nao
2025-03-15,dicionarios,iteracao,"Como percorrer um dicionario?",sim,2,sim
2025-03-20,strings,fatiamento,"Nao entendi como funciona slicing",sim,2,sim
2025-03-25,strings,metodos_string,"Quando usar split e join?",sim,2,nao
2025-04-01,funcoes,parametros,"Qual a diferenca entre parametro e argumento?",sim,2,sim
2025-04-05,funcoes,retorno,"Nao entendi para que serve return",sim,2,sim
2025-04-10,funcoes,escopo,"O que e escopo de variaveis?",sim,3,sim
2025-04-15,tratamento_erros,try_except,"Como evitar que o programa pare com erro?",sim,2,nao
2025-04-20,arquivos,open,"Erro ao abrir arquivo txt",sim,2,sim
2025-04-25,arquivos,leitura_arquivos,"Como ler um arquivo linha por linha?",sim,2,nao
2025-05-01,modulos,import,"Nao entendi como funcionam imports",sim,2,sim
2025-05-05,bibliotecas,pip,"Recebi ModuleNotFoundError",sim,2,sim
2025-05-10,poo,classes,"Nao entendi o conceito de classes",nao,3,nao
2025-05-15,poo,objetos,"Qual a diferenca entre classe e objeto?",nao,3,nao
2025-05-20,poo,metodos,"Como criar metodos em uma classe?",nao,3,nao
2025-05-25,poo,heranca,"Nao entendi heranca em Python",nao,4,nao
2025-06-01,recursao,recursao,"Recebi RecursionError",nao,4,nao
2025-06-05,testes,assert,"Como usar assert para validar resultados?",sim,3,nao
2025-06-10,estruturas_dados,sets,"Quando devo usar um set?",sim,2,sim
2025-06-15,compreensao_listas,list_comprehension,"Nao entendi list comprehension",nao,3,nao
2025-06-18,tipos_de_dados,tipagem,"Recebi TypeError ao somar um numero com uma string",sim,1,sim

ERROS COMUNS (data/erros_comuns.csv):
erro_comum,topico,nivel,explicacao_simples,dica_guiada
"SyntaxError","sintaxe_basica","iniciante","Há um erro na forma como o código foi escrito e o Python não consegue interpretá-lo.","Observe a linha indicada pelo erro. Está faltando algum caractere, como dois pontos, parênteses ou aspas?"
"IndentationError","sintaxe_basica","iniciante","A indentação está incorreta ou inconsistente.","Essa linha faz parte de um bloco como if, for ou while? A indentação está alinhada com as demais?"
"TabError","sintaxe_basica","iniciante","Há mistura de tabs e espaços na indentação.","Você está usando apenas espaços ou apenas tabs para indentar o código?"
"NameError: name is not defined","variaveis","iniciante","Uma variável ou função está sendo usada antes de ser definida.","Essa variável ou função foi criada antes dessa linha? O nome está escrito exatamente igual?"
"UnboundLocalError","variaveis","intermediario","Uma variável local está sendo acessada antes de receber um valor.","Essa variável recebeu algum valor dentro da função antes de ser utilizada?"
"TypeError","tipos_de_dados","iniciante","Foi realizada uma operação entre tipos incompatíveis.","Os valores envolvidos na operação possuem tipos compatíveis? Você verificou usando type()?"
"TypeError: can only concatenate str","tipos_de_dados","iniciante","Você tentou juntar texto com outro tipo de dado sem conversão.","Os dois valores possuem o mesmo tipo? Como você poderia converter um deles?"
"ValueError","tipos_de_dados","iniciante","O valor fornecido não é válido para a operação solicitada.","O conteúdo dessa variável está no formato esperado para essa operação?"
"ZeroDivisionError","operacoes_matematicas","iniciante","O código tentou dividir um número por zero.","Existe alguma situação em que o divisor possa valer zero?"
"OverflowError","operacoes_matematicas","avancado","O cálculo gerou um número maior do que o suportado.","Os valores utilizados nesse cálculo estão crescendo sem controle?"
"IndexError: list index out of range","estruturas_dados","iniciante","Você tentou acessar uma posição que não existe na lista.","Quantos itens essa lista possui e qual posição você está tentando acessar?"
"KeyError","estruturas_dados","intermediario","Você tentou acessar uma chave que não existe em um dicionário.","Essa chave realmente existe no dicionário? Já verificou as chaves disponíveis?"
"AttributeError","poo","intermediario","Você chamou um atributo ou método que não existe nesse objeto.","Tem certeza de que esse objeto é do tipo esperado? Já verificou usando type()?"
"ImportError","modulos","iniciante","O Python não conseguiu importar o recurso solicitado.","O nome do item importado existe realmente nesse módulo?"
"ModuleNotFoundError","ambiente_dev","iniciante","O módulo solicitado não foi encontrado no ambiente.","A biblioteca foi instalada corretamente? O nome está escrito corretamente?"
"FileNotFoundError","arquivos","iniciante","O arquivo informado não foi encontrado.","O caminho e o nome do arquivo estão corretos?"
"PermissionError","arquivos","intermediario","O sistema não permitiu o acesso ao recurso solicitado.","Você possui permissão para acessar esse arquivo ou pasta?"
"IsADirectoryError","arquivos","intermediario","Uma pasta foi utilizada onde era esperado um arquivo.","O caminho informado aponta para um arquivo ou para uma pasta?"
"NotADirectoryError","arquivos","intermediario","Parte do caminho informado não corresponde a um diretório.","Todos os diretórios desse caminho realmente existem?"
"EOFError","entrada_saida","intermediario","A entrada de dados terminou antes do esperado.","O programa recebeu todas as informações necessárias para continuar?"
"AssertionError","testes","intermediario","Uma condição que deveria ser verdadeira falhou.","A condição utilizada no assert deveria realmente ser satisfeita?"
"RuntimeError","execucao","intermediario","Ocorreu um erro durante a execução do programa.","Existe alguma situação inesperada acontecendo no fluxo de execução?"
"RecursionError: maximum recursion depth","recursao","avancado","A função recursiva ultrapassou o limite de chamadas permitido.","Sua função possui uma condição de parada que realmente é alcançada?"
"MemoryError","performance","avancado","O programa tentou utilizar mais memória do que o disponível.","Você está criando listas, dicionários ou objetos muito grandes?"
"StopIteration","iteradores","intermediario","O iterador chegou ao fim dos elementos disponíveis.","Ainda existem elementos para serem percorridos?"
"GeneratorExit","iteradores","avancado","O gerador foi encerrado durante a execução.","O gerador foi interrompido manualmente ou por outro processo?"
"UnicodeEncodeError","strings","intermediario","Não foi possível converter caracteres para a codificação escolhida.","A codificação utilizada suporta todos os caracteres presentes no texto?"
"UnicodeDecodeError","strings","intermediario","Não foi possível interpretar corretamente os bytes recebidos.","A codificação usada para ler o arquivo é a mesma usada para salvá-lo?"
"ConnectionError","redes","intermediario","Ocorreu uma falha na conexão com um serviço externo.","O serviço está acessível e a conexão com a internet está funcionando?"
"TimeoutError","redes","intermediario","A operação demorou mais do que o tempo permitido.","O serviço está respondendo lentamente ou a rede está instável?"
"BrokenPipeError","redes","avancado","A comunicação foi interrompida porque a outra ponta da conexão foi encerrada.","A conexão ainda estava ativa quando os dados foram enviados?"
"KeyboardInterrupt","execucao","iniciante","A execução foi interrompida manualmente pelo usuário.","O programa estava preso em um loop ou demorando mais do que o esperado?"
"FloatingPointError","operacoes_matematicas","avancado","Ocorreu um erro relacionado a operações com números de ponto flutuante.","Os cálculos estão gerando valores inválidos ou inesperados?"
"OSError","sistema","intermediario","O sistema operacional reportou um erro durante a execução.","O recurso solicitado existe e está acessível no sistema?"
"ReferenceError","memoria","avancado","Uma referência aponta para um objeto que já não existe mais.","O objeto referenciado ainda está disponível na memória?"
"BufferError","memoria","avancado","Uma operação não pôde ser concluída devido ao estado atual de um buffer.","Existe algum outro processo utilizando esse buffer?"
"LookupError","estruturas_dados","intermediario","O elemento procurado não foi encontrado.","O valor que você está tentando localizar realmente existe?"
"SystemExit","execucao","intermediario","O programa solicitou seu próprio encerramento.","Existe alguma chamada para exit() ou sys.exit() sendo executada?"
"NotImplementedError","poo","intermediario","Um método foi declarado mas ainda não recebeu implementação.","Essa funcionalidade deveria ter sido implementada em uma classe derivada?"
"ConnectionRefusedError","redes","intermediario","O servidor recusou a conexão solicitada.","O serviço está realmente em execução e aceitando conexões?"
"TimeoutExpired","processos","intermediario","Um processo excedeu o tempo limite permitido.","Essa tarefa está demorando mais do que deveria para terminar?"
"ChildProcessError","processos","avancado","Ocorreu um erro ao manipular processos filhos.","O processo filho foi criado e encerrado corretamente?"
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """Você é o Pierre, um mentor da área de Progrmação em Python, amigável e didático.

OBJETIVO:
Tirar dúvidas e ajudar o desenvolvedor a encontrar soluções para seus problemas de forma guiada, completa e didática, analisando o
histórico do desenvolvedor para uma reposta mais contextualizada.

REGRAS:
1. Você deve responder apenas questões relacionadas a programação em Python, nenhum assunto fora desse meio é permitido ser dito
e caso alguma pergunta fora desse meio seja feita diga algo parecido com: "Sou especializado em programação em Python e não tenho
informações sobre previsão do tempo. Posso ajudar com algo relacionado à programação em Python?"
2. Você deve responder apenas questões relacionadas a programação em Python, nenhuma outra linguagem de programação é permitida
ser dita e caso outra linguagem de programação seja solicitada diga algo parecido com: "Não tenho informações sobre outras
linguagens de programação, posso te explicar de acordo com o Python..."..
3. Sempre consulte o histórico de dúvidas do desenvolvedor para respostas mais personalizadas.
4. Utilize por padrão o método de Scaffolding, fazer perguntas antes de revelar a solução, em suas explicações, como um mentor
pensando no melhor para o seu aluno, porém caso seja solicitado explicitamente pelo desenvolvedor que ele quer a resposta de forma
direta, responda de forma direta sem o uso do Scaffolding.
5. Utilize o scaffolding e a solução do problema do usuário na mesma resposta.
6. Caso você não saiba de algo, admita: "Não tenho informação sobre esse assunto...".
7. Utilize uma linguagem simples e de acordo com o nível de conhecimento do desenvolvedor.
8. Em suas explicações seja repleto de conceitos, não poupe definições e sempre utilize exemplos fáceis e práticos para
um melhor entendimento.
"""

# ============ CHAMAR OLLAMA ============
def perguntar(msg):
    prompt = f"""
    {SYSTEM_PROMPT}

    CONTEXTO DO CLIENTE:
    {contexto}

    Pergunta: {msg}"""

    r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False})
    return r.json()['response']

# ============ INTERFACE ============
st.title("🎓 Pierre, Seu Mentor de Python")

if pergunta := st.chat_input("Sua dúvida sobre Python..."):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
