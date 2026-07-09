import os, re as _re, json, math, random, datetime, time, unicodedata as _ud

vitimas:    list[dict] = []
equipes:    list[dict] = []
logs:       list[dict] = []
ocorrencias:list[dict] = []

COR = {
    "reset":"[0m","bold":"[1m","dim":"[2m",
    "vermelho":"[91m","laranja":"[93m","verde":"[92m","azul":"[95m",
    "cinza":"[90m","ciano":"[35m","magenta":"[35m","branco":"[97m",
    "bg_azul":"[45m","bg_verm":"[41m","bg_verde":"[42m",
}

def cor(texto, c):
    if os.name == "nt":
        try:
            import ctypes; ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
        except Exception: return texto
    return f"\033{COR.get(c,'')}{texto}\033{COR['reset']}"

def limpar_tela():   os.system("cls" if os.name == "nt" else "clear")
def pausar(msg="  Pressione (ENTER) para continuar"): input(f"\n{cor(msg,'cinza')}")

_ANSI = _re.compile(r"\x1b\[[0-9;]*m")

def _wlen(s):
    limpa = _ANSI.sub("", s)
    return sum(2 if _ud.east_asian_width(c) in ("W","F") else 1 for c in limpa)

def _pad(s, total, align="<"):
    diff = max(0, total - _wlen(s))
    if align == ">": return " "*diff + s
    if align == "^": l=diff//2; return " "*l + s + " "*(diff-l)
    return s + " "*diff

def cabecalho():
    agora   = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
    criticos= sum(1 for v in vitimas if v["score"]>=85 and v["status"]=="Aguardando resgate")
    eq_disp = sum(1 for e in equipes if e["status"]=="Disponível")
    print(cor("═"*78, "azul"))
    print(cor("   DISASTERLINK  ","bold") + cor("Plataforma de Resposta a Emergências","branco")
          + " "*max(1, 44-len(agora)) + cor(agora,"cinza"))
    print(cor("  FIAP Global Solution 2026 — Space Connect","cinza"))
    print(cor("─"*78,"azul"))
    print(f"  Vítimas: {cor(str(len(vitimas)),'branco')}"
          f"    Críticas: {cor(str(criticos),'vermelho' if criticos>0 else 'cinza')}"
          f"    Equipes disponíveis: {cor(str(eq_disp),'verde')}"
          f"    Logs: {cor(str(len(logs)),'cinza')}")
    print(cor("═"*78,"azul"))

def titulo(icone, txt, sub=""):
    print(); print(cor("─"*78,"ciano"))
    print(cor(f"  {icone}  {txt}" if icone else f"  {txt}","bold"))
    if sub: print(cor(f"     {sub}","cinza"))
    print(cor("─"*78,"ciano")); print()

def opcao(tecla, desc, det="", cor_tecla="ciano", desabilitado=False):
    if desabilitado:
        print(f"  {cor(f'[{tecla}]','cinza')}  {cor(desc,'cinza')}")
    else:
        det_fmt = f"  {cor(det,'cinza')}" if det else ""
        print(f"  {cor(f'[{tecla}]',cor_tecla)}  {desc}{det_fmt}")

def secao(txt):
    print(); print(f"  {cor('◈','ciano')}  {cor(txt.upper(),'bold')}")
    print(f"  {'─'*(len(txt)+5)}")

def dica(txt):   print(f"\n  {cor('','azul')} {cor(txt,'cinza')}")
def aviso(txt):  print(f"\n  {cor('  ATENÇÃO:','laranja')} {cor(txt,'laranja')}")
def sucesso(txt):print(f"\n  {cor('','verde')}  {cor(txt,'verde')}")
def erro(txt):   print(f"\n  {cor('  ERRO:','vermelho')} {cor(txt,'vermelho')}")
def alerta_critico(txt): print(f"\n  {cor('  '+txt,'vermelho')}")

def rodape(dica_txt=""):
    print(); print(cor("  "+"─"*74,"cinza"))
    if dica_txt: print(f"  {cor('ℹ','azul')}  {cor(dica_txt,'cinza')}")
    print()

def log(acao, detalhe=""):
    logs.append({"hora": datetime.datetime.now().strftime("%H:%M:%S"),
                 "acao": acao, "detalhe": detalhe})

def ler_opcao(validas, prompt="  Opção"):
    up = [str(o).upper() for o in validas]
    print(f"\n  {cor('Opções:','cinza')} {cor('  '.join(str(o) for o in validas),'ciano')}")
    while True:
        try:
            e = input(f"  {cor('▶','ciano')} {prompt}: ").strip().upper()
            if e in up: return e
            print(f"  {cor('  Opção inválida. Tente:','laranja')} {', '.join(str(o) for o in validas)}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Encerrando..."); return "0"

def ler_int(prompt, minimo=0, maximo=9999):
    while True:
        try:
            v = int(input(f"  {cor('▶','ciano')} {prompt} {cor(f'({minimo}–{maximo})','cinza')}: ").strip())
            if minimo <= v <= maximo: return v
            print(f"  {cor(f'  Digite entre {minimo} e {maximo}.','laranja')}")
        except ValueError: print(f"  {cor('  Apenas números inteiros.','laranja')}")
        except (KeyboardInterrupt, EOFError): return minimo

def ler_float(prompt, minimo=-999.0, maximo=999.0):
    while True:
        try:
            v = float(input(f"  {cor('▶','ciano')} {prompt} {cor(f'({minimo}/{maximo})','cinza')}: "
                            ).strip().replace(",","."))
            if minimo <= v <= maximo: return v
            print(f"  {cor(f'  Fora do intervalo [{minimo}, {maximo}].','laranja')}")
        except ValueError: print(f"  {cor('  Use ponto ou vírgula decimal.','laranja')}")
        except (KeyboardInterrupt, EOFError): return minimo

def ler_texto(prompt, max_len=100, exemplo=""):
    ex = f" {cor(f'ex: {exemplo}','cinza')}" if exemplo else ""
    while True:
        try:
            v = input(f"  {cor('▶','ciano')} {prompt}{ex}: ").strip()
            if v: return v[:max_len]
            print(f"  {cor('  Este campo não pode ficar em branco.','laranja')}")
        except (KeyboardInterrupt, EOFError): return "Desconhecido"

def ler_sim_nao(prompt):
    while True:
        r = input(f"  {cor('▶','ciano')} {prompt} {cor('[S/N]','ciano')}: ").strip().upper()
        if r in ("S","N"): return r == "S"
        print(f"  {cor('  Digite S para Sim ou N para Não.','laranja')}")

def distancia(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2-lat1); dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def calc_eta(dist_km, vel=40.0):
    m = (dist_km/vel)*60
    return f"{m:.0f} min" if m < 60 else f"{int(m//60)}h {int(m%60)}min"

def barra(score, largura=20):
    n = int((score/100)*largura); c = urgencia_cor(score)
    return cor("█"*n, c) + cor("░"*(largura-n),"cinza")

TIPOS_EMERGENCIA = {
    "1":("Soterrado / Preso",40), "2":("Ferimento Grave",38),
    "3":("Ferimento Leve",20),    "4":("Risco de Afogamento",42),
    "5":("Perdido / Sem Comunicação",25), "6":("Necessidade Médica Crônica",30),
    "7":("Vulnerável (Idoso/Criança)",28),"8":("Intoxicação / Inalação de Gás",35),
}
CANAIS_DETECCAO = {
    "1":"Portal WiFi (Captive Portal)", "2":"SMS via Rede Satelital",
    "3":"Botão SOS LoRa",              "4":"Sensor Térmico / Câmera IR",
    "5":"Microfone Acústico Direcional","6":"Radar UWB Respiratório",
    "7":"Rastreamento Passivo BLE/WiFi","8":"Reporte Manual / Terceiros",
}
STATUS_VITIMA = ["Aguardando resgate","Equipe a caminho","Em atendimento","Resgatado","Óbito"]
STATUS_COR    = {"Aguardando resgate":"laranja","Equipe a caminho":"azul",
                 "Em atendimento":"ciano","Resgatado":"verde","Óbito":"cinza"}

def score_urgencia(tipo, horas, vulneravel, ferimentos):
    _, pts = TIPOS_EMERGENCIA[tipo]
    return min(100, pts + min(28,int((min(horas,24)/24)*28)) + (20 if vulneravel else 0) + min(10,ferimentos*2))

def urgencia(score):
    if score>=85: return "[!!!] CRITICO"
    if score>=60: return "[ !! ] ALTO  "
    if score>=35: return "[  ! ] MEDIO "
    return "[    ] BAIXO "

def urgencia_cor(score):
    return "vermelho" if score>=85 else "laranja" if score>=35 else "verde"

DADOS_DEMO_VITIMAS = [
    {"nome":"Abc",              "tipo":"1","lat":-23.5505,"lon":-46.6333,"canal":"Portal WiFi (Captive Portal)","horas":4.5,"vulneravel":True, "ferimentos":3,"obs":"Soterrada, responde a voz"},
    {"nome":"Corinthians",      "tipo":"2","lat":-23.5620,"lon":-46.6450,"canal":"SMS via Rede Satelital",      "horas":2.0,"vulneravel":False,"ferimentos":2,"obs":"Ferimento na perna"},
    {"nome":"Criança desconhecida","tipo":"7","lat":-23.5480,"lon":-46.6200,"canal":"Sensor Térmico / Câmera IR","horas":6.0,"vulneravel":True, "ferimentos":1,"obs":"Detectada por sensor térmico"},
    {"nome":"Teste",            "tipo":"4","lat":-23.5700,"lon":-46.6100,"canal":"Botão SOS LoRa",              "horas":1.5,"vulneravel":False,"ferimentos":0,"obs":"Risco de afogamento no rio"},
    {"nome":"Desconhecido",     "tipo":"6","lat":-23.5400,"lon":-46.6500,"canal":"Reporte Manual / Terceiros",  "horas":3.0,"vulneravel":True, "ferimentos":1,"obs":"Diabética sem insulina"},
]
DADOS_DEMO_EQUIPES = [
    {"nome":"Bombeiros",   "especialidade":"Busca e Resgate Terrestre",        "membros":6,"velocidade":45,"lat":-23.5550,"lon":-46.6400},
    {"nome":"Médicos",     "especialidade":"Atendimento Médico de Emergência", "membros":4,"velocidade":60,"lat":-23.5600,"lon":-46.6300},
    {"nome":"Bombeiros 2", "especialidade":"Combate a Incêndio / USAR",        "membros":8,"velocidade":50,"lat":-23.5450,"lon":-46.6250},
]

def carregar_dados_demo():
    global vitimas, equipes
    limpar_tela()
    titulo("","CARREGAR DADOS DE DEMONSTRAÇÃO","Popula o sistema com cenário realista pré-configurado")
    print(f"  {cor('Este modo carrega:','cinza')}")
    print(f"  {cor('•','ciano')} {len(DADOS_DEMO_VITIMAS)} vítimas com diferentes níveis de urgência")
    print(f"  {cor('•','ciano')} {len(DADOS_DEMO_EQUIPES)} equipes de resgate prontas")
    print(f"  {cor('•','ciano')} Coordenadas GPS reais na região de São Paulo\n")
    if (vitimas or equipes):
        aviso("Dados existentes serão substituídos!")
        if not ler_sim_nao("Confirma a substituição"):
            print(f"\n  {cor('Operação cancelada.','cinza')}"); pausar(); return
    agora = datetime.datetime.now(); vitimas.clear(); equipes.clear()
    for i,d in enumerate(DADOS_DEMO_VITIMAS):
        sc = score_urgencia(d["tipo"],d["horas"],d["vulneravel"],d["ferimentos"])
        vitimas.append({"id":f"VT{i+1:04d}","nome":d["nome"],"tipo":d["tipo"],
            "tipo_desc":TIPOS_EMERGENCIA[d["tipo"]][0],"lat":d["lat"],"lon":d["lon"],
            "canal":d["canal"],"horas_sem_resposta":d["horas"],"vulneravel":d["vulneravel"],
            "ferimentos":d["ferimentos"],"observacoes":d["obs"],"score":sc,
            "nivel":urgencia(sc),"status":"Aguardando resgate",
            "registrado_em":agora.strftime("%d/%m/%Y %H:%M"),
            "atualizado_em":agora.strftime("%d/%m/%Y %H:%M")})
    for i,d in enumerate(DADOS_DEMO_EQUIPES):
        equipes.append({"id":f"EQ{i+1:03d}","nome":d["nome"],"especialidade":d["especialidade"],
            "membros":d["membros"],"velocidade_kmh":d["velocidade"],"lat":d["lat"],"lon":d["lon"],
            "status":"Disponível","vitima_designada":None,
            "cadastrado_em":agora.strftime("%d/%m/%Y %H:%M")})
    log("Dados demo carregados", f"{len(vitimas)} vítimas, {len(equipes)} equipes")
    print(f"\n  {cor('─ Resultado '+'─'*44,'verde')}")
    for v in vitimas:
        print(f"    {v['id']} — {v['nome'][:28]:<28}  Score: {cor(str(v['score']),'branco')}")
    print(f"  {cor('─'*56,'verde')}")
    sucesso(f"{len(vitimas)} vítimas e {len(equipes)} equipes carregadas com sucesso!")
    dica("Experimente: Módulo 1 → Lista por urgência  |  Módulo 3 → Designar equipes")
    pausar()

def menu_registro_vitimas():
    while True:
        limpar_tela(); cabecalho()
        titulo("","MÓDULO 1 — REGISTRO E TRIAGEM DE VÍTIMAS","Cadastro, consulta e atualização de vítimas")
        total=len(vitimas); criticos=sum(1 for v in vitimas if v["score"]>=85)
        aguardando=sum(1 for v in vitimas if v["status"]=="Aguardando resgate")
        resgatados=sum(1 for v in vitimas if v["status"]=="Resgatado")
        print(f"  {cor('─'*74,'cinza')}")
        print(f"  Registradas: {cor(str(total),'branco')}    Críticas: {cor(str(criticos),'vermelho')}"
              f"    Aguardando: {cor(str(aguardando),'laranja')}    Resgatadas: {cor(str(resgatados),'verde')}")
        print(f"  {cor('─'*74,'cinza')}\n")
        opcao("1","Registrar nova vítima",    " preencher ficha de campo")
        opcao("2","Listar por urgência",       " ranking do mais crítico ao menos")
        opcao("3","Atualizar status de vítima"," alterar estado de resgate")
        opcao("4","Pesquisar vítima",          " busca por nome ou ID")
        opcao("5","Ficha completa de vítima",  " todos os dados + equipe designada")
        print(); opcao("0","Voltar ao menu principal",cor_tecla="cinza")
        rodape("IDs no formato VT0001. Use [2] para ver todos os IDs registrados.")
        match ler_opcao(["1","2","3","4","5","0"]):
            case "1": registrar_vitima()
            case "2": listar_vitimas()
            case "3": atualizar_status_vitima()
            case "4": pesquisar_vitima()
            case "5": detalhes_vitima()
            case "0": break

def registrar_vitima():
    limpar_tela()
    titulo("","REGISTRAR NOVA VÍTIMA","Preencha com informações repassadas pela vítima ou equipe de campo")
    id_v = f"VT{len(vitimas)+1:04d}"; agora = datetime.datetime.now()
    print(f"  {cor('ID gerado:','cinza')} {cor(id_v,'ciano')}   {cor(agora.strftime('%d/%m/%Y %H:%M:%S'),'cinza')}\n")
    nome = ler_texto("Nome da vítima (ou 'Desconhecido')", exemplo="Caique")
    secao("Tipo de Emergência")
    print(f"  {'Nº':<4} {'Descrição':<35} {'Urgência'}")
    print(f"  {'─'*60}")
    for k,(desc,pts) in TIPOS_EMERGENCIA.items():
        print(f"  {cor(f'[{k}]','ciano'):<4}  {desc:<35} {cor('█'*(pts//4),urgencia_cor(pts*2))} {cor(str(pts),'cinza')}")
    tipo = ler_opcao(TIPOS_EMERGENCIA.keys(),"Tipo de emergência")
    secao("Localização GPS")
    dica("Google Maps: clique no local → lat, lon aparece na barra de endereço")
    print(f"  {cor('Exemplo SP:','cinza')} lat -23.5505  /  lon -46.6333")
    lat = ler_float("Latitude ",-90,90); lon = ler_float("Longitude",-180,180)
    secao("Canal de Detecção — como o alerta chegou?")
    for k,desc in CANAIS_DETECCAO.items(): print(f"  {cor(f'[{k}]','ciano')}  {desc}")
    canal = ler_opcao(CANAIS_DETECCAO.keys(),"Canal de detecção")
    secao("Dados de Triagem")
    horas      = ler_float("Horas sem resposta (ex: 2.5)",0,72)
    vulneravel = ler_sim_nao("É vulnerável? (Idoso / Criança / Doente crônico)")
    ferimentos = ler_int("Número de ferimentos visíveis",0,5)
    print(f"\n  {cor('▶','ciano')} Observações adicionais {cor('(ENTER para pular)','cinza')}: ", end="")
    obs = input("").strip()
    sc = score_urgencia(tipo,horas,vulneravel,ferimentos); nv = urgencia(sc)
    vitimas.append({"id":id_v,"nome":nome,"tipo":tipo,"tipo_desc":TIPOS_EMERGENCIA[tipo][0],
        "lat":lat,"lon":lon,"canal":CANAIS_DETECCAO[canal],"horas_sem_resposta":horas,
        "vulneravel":vulneravel,"ferimentos":ferimentos,"observacoes":obs,"score":sc,"nivel":nv,
        "status":"Aguardando resgate","registrado_em":agora.strftime("%d/%m/%Y %H:%M"),
        "atualizado_em":agora.strftime("%d/%m/%Y %H:%M")})
    log("Vítima registrada",f"{id_v} | {nome} | Score {sc} | {nv}")
    print(f"\n  {cor('═'*59,'verde')}")
    print(f"  {cor('  Vítima registrada com sucesso!','bold')}")
    print(f"  {cor('─'*59,'verde')}")
    for label,val in [("ID",cor(id_v,"ciano")),("Nome",nome[:50]),
                      ("Emergência",TIPOS_EMERGENCIA[tipo][0][:48]),
                      ("GPS",f"({lat:.4f}, {lon:.4f})"),
                      ("Urgência",f"{barra(sc)} {cor(f'{sc}/100','branco')}  {cor(nv,urgencia_cor(sc))}")]:
        print(f"  {f'  {label}:':<14}{val}")
    print(f"  {cor('═'*59,'verde')}")
    if sc>=85:
        alerta_critico("Vítima CRÍTICA — acione equipe imediatamente!")
        print(f"  {cor(' Vá ao Módulo 3 → Designar Equipes','azul')}")
    pausar()

def listar_vitimas():
    limpar_tela()
    titulo("","LISTA DE VÍTIMAS — ORDENADAS POR URGÊNCIA","Da mais crítica à menos urgente")
    if not vitimas: aviso("Nenhuma vítima registrada ainda."); pausar(); return
    ord_v = sorted(vitimas, key=lambda v:v["score"],reverse=True)
    C_ID,C_NOME,C_TIPO,C_URG = 8,22,28,14
    print(f"  {_pad(cor('ID','cinza'),C_ID)} {_pad(cor('Nome','cinza'),C_NOME)} "
          f"{_pad(cor('Emergência','cinza'),C_TIPO)} {_pad(cor('Urgência','cinza'),C_URG)}  {cor('Status','cinza')}")
    print(f"  {'─'*78}")
    for v in ord_v:
        sc_col = f"{barra(v['score'],10)} {cor(str(v['score']).rjust(3),urgencia_cor(v['score']))}"
        print(f"  {_pad(cor(v['id'],'ciano'),C_ID)} {_pad(v['nome'][:C_NOME],C_NOME)} "
              f"{_pad(v['tipo_desc'][:C_TIPO],C_TIPO)} {_pad(sc_col,C_URG+8)}  "
              f"{cor(v['status'],STATUS_COR.get(v['status'],'cinza'))}")
    print(f"  {'─'*78}")
    res = sum(1 for v in vitimas if v["status"]=="Resgatado")
    print(f"\n  Total: {cor(str(len(vitimas)),'branco')}    Resgatadas: {cor(str(res),'verde')}"
          f"    Aguardando: {cor(str(len(vitimas)-res),'laranja')}")
    pausar()

def atualizar_status_vitima():
    limpar_tela()
    titulo("","ATUALIZAR STATUS DE VÍTIMA","Altere o estado de resgate de uma vítima registrada")
    if not vitimas: aviso("Nenhuma vítima registrada."); pausar(); return
    dica("Use o ID no formato VT0001, ou consulte a lista [2] para encontrar o ID.")
    id_busca = ler_texto("ID da vítima",exemplo="VT0001").upper()
    lista = [v for v in vitimas if v["id"]==id_busca]
    if not lista: erro(f"Vítima '{id_busca}' não encontrada."); pausar(); return
    v = lista[0]
    print(f"\n  {cor('Vítima encontrada:','verde')}")
    print(f"  {cor('─'*49,'ciano')}")
    print(f"    {v['id']}  —  {cor(v['nome'],'branco')}")
    print(f"    {barra(v['score'])}  {v['score']}/100  {cor(v['nivel'],urgencia_cor(v['score']))}")
    print(f"    Status atual: {cor(v['status'],STATUS_COR.get(v['status'],'cinza'))}")
    print(f"  {cor('─'*49,'ciano')}")
    secao("Selecione o novo status")
    for i,s in enumerate(STATUS_VITIMA,1):
        mk = f"  {cor('< atual','verde')}" if s==v["status"] else ""
        print(f"  {cor(f'[{i}]','ciano')}  {s}{mk}")
    idx = ler_int("Novo status",1,5)
    ant = v["status"]; v["status"]=STATUS_VITIMA[idx-1]
    v["atualizado_em"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    log("Status atualizado",f"{v['id']} | {ant} -> {v['status']}")
    sucesso(f"Status: {cor(ant,'cinza')}  →  {cor(v['status'],STATUS_COR.get(v['status'],'ciano'))}")
    pausar()

def pesquisar_vitima():
    limpar_tela()
    titulo("","PESQUISAR VÍTIMA","Busca por nome parcial ou ID completo")
    termo = ler_texto("Nome ou ID de busca").lower()
    enc = [v for v in vitimas if termo in v["nome"].lower() or termo in v["id"].lower()]
    if not enc:
        aviso(f"Nenhum resultado para '{termo}'.")
    else:
        print(f"\n  {cor(f'  {len(enc)} resultado(s) encontrado(s)','verde')}\n")
        for v in enc:
            nc=urgencia_cor(v["score"]); sc=STATUS_COR.get(v["status"],"cinza")
            print(f"  {cor('─'*53,'ciano')}")
            print(f"    {cor(v['id'],'ciano')}  —  {cor(v['nome'],'branco')}")
            print(f"    {v['tipo_desc']}  │  Score: {cor(str(v['score']),nc)}  │  {cor(v['nivel'],nc)}")
            print(f"    {cor(v['status'],sc)}  │  GPS: ({v['lat']:.4f}, {v['lon']:.4f})  │  {v['registrado_em']}")
            print(f"    Canal: {v['canal']}")
            print(f"  {cor('─'*53,'ciano')}\n")
    pausar()

def detalhes_vitima():
    limpar_tela()
    titulo("","FICHA COMPLETA DA VÍTIMA","Todos os dados registrados + equipe designada")
    if not vitimas: aviso("Nenhuma vítima registrada."); pausar(); return
    id_busca = ler_texto("ID da vítima",exemplo="VT0001").upper()
    v = next((x for x in vitimas if x["id"]==id_busca), None)
    if not v: erro(f"Vítima '{id_busca}' não encontrada."); pausar(); return
    nc=urgencia_cor(v["score"]); sc=STATUS_COR.get(v["status"],"cinza")
    print(f"\n  {cor('═'*62,'ciano')}")
    print(f"  {cor('  FICHA DA VÍTIMA','bold')}")
    print(f"  {cor('─'*62,'ciano')}")
    def fld(label,val,c="branco"):
        pad=" "*max(0,18-_wlen(f"{label}:")-2)
        print(f"    {cor(f'{label}:','cinza')}{pad}{cor(str(val),c)}")
    fld("ID",v["id"]); fld("Nome",v["nome"]); fld("Emergência",v["tipo_desc"])
    fld("GPS",f"lat {v['lat']:.5f}  /  lon {v['lon']:.5f}")
    fld("Canal detecção",v["canal"]); fld("Horas s/ resposta",f"{v['horas_sem_resposta']:.1f}h")
    fld("Vulnerável","Sim" if v["vulneravel"] else "Não","laranja" if v["vulneravel"] else "verde")
    fld("Ferimentos",v["ferimentos"]); fld("Observações",v["observacoes"] or "—")
    print(f"    {cor('Score triagem:','cinza')}    {barra(v['score'])}  {cor(str(v['score']),nc)}/100  {cor(v['nivel'],nc)}")
    fld("Status",v["status"],sc); fld("Registrado em",v["registrado_em"]); fld("Atualizado em",v["atualizado_em"])
    eq = next((e for e in equipes if e.get("vitima_designada")==v["id"]),None)
    print(f"  {cor('─'*62,'ciano')}")
    if eq:
        d=distancia(v["lat"],v["lon"],eq["lat"],eq["lon"]); e=calc_eta(d,eq["velocidade_kmh"])
        fld("Equipe",f"{eq['id']} — {eq['nome']}","ciano"); fld("Distância / ETA",f"{d:.1f} km  │  ETA: {e}","verde")
    else:
        fld("Equipe designada","Nenhuma — use Módulo 3 para designar","laranja")
    print(f"  {cor('═'*62,'ciano')}")
    pausar()

CANAIS_COMM = [
    {"id":1,"nome":"Satélite Iridium SBD",  "prioridade":1,"banda":"340 bytes/msg","latencia":"~90s", "custo":"US$ 0.04/msg","taxa_falha":0.05},
    {"id":2,"nome":"Mesh LoRa entre kits",  "prioridade":2,"banda":"50 bytes/pkt", "latencia":"~30s", "custo":"Gratuito",    "taxa_falha":0.15},
    {"id":3,"nome":"4G/5G (failover)",       "prioridade":3,"banda":"Banda larga",  "latencia":"~2s",  "custo":"R$ 35/mês",   "taxa_falha":0.35},
    {"id":4,"nome":"Rádio HF (ondas curtas)","prioridade":4,"banda":"1.2 kbps",    "latencia":"~5min","custo":"Gratuito",    "taxa_falha":0.25},
    {"id":5,"nome":"WiFi Captive Portal",    "prioridade":5,"banda":"Local apenas", "latencia":"< 1s", "custo":"Gratuito",    "taxa_falha":0.50},
]

def menu_simulador_comunicacao():
    while True:
        limpar_tela(); cabecalho()
        titulo("","MÓDULO 2 — SIMULADOR DE CANAIS DE COMUNICAÇÃO","Hierarquia: Satélite → LoRa → 4G → HF → WiFi")
        opcao("1","Status dos canais",         " verificar disponibilidade em tempo real")
        opcao("2","Simular envio de socorro",  " testar transmissão com failover automático")
        opcao("3","Simular falha em cascata",  " ver sistema sob condições extremas")
        opcao("4","Calcular custo de operação"," estimativa de gastos Iridium vs gratuitos")
        opcao("5","Comparativo técnico",       " tabela de specs de todos os canais")
        print(); opcao("0","Voltar ao menu principal",cor_tecla="cinza")
        rodape("O sistema usa failover automático: se um canal falhar, o próximo assume.")
        match ler_opcao(["1","2","3","4","5","0"]):
            case "1": status_canais()
            case "2": simular_transmissao()
            case "3": simular_failover()
            case "4": calcular_custo_transmissao()
            case "5": comparativo_canais()
            case "0": break

def status_canais():
    limpar_tela()
    titulo("","STATUS DOS CANAIS EM TEMPO REAL","Verificação de disponibilidade de cada canal")
    print(f"  {cor('Consultando canais...','cinza')}\n"); time.sleep(0.4)
    C_PRI,C_NOME,C_BANDA,C_LAT,C_CUSTO = 5,26,16,9,16
    print(f"  {_pad('Pri',C_PRI)} {_pad(cor('Canal','cinza'),C_NOME)} "
          f"{_pad(cor('Banda','cinza'),C_BANDA)} {_pad(cor('Latência','cinza'),C_LAT)} "
          f"{_pad(cor('Custo','cinza'),C_CUSTO)} {cor('Status','cinza')}")
    print(f"  {'─'*78}")
    for c in CANAIS_COMM:
        r = random.random()
        estado = (cor("[OFF]   ","vermelho") if r < c["taxa_falha"]*0.3
                  else cor("[DEG]   ","laranja") if r < c["taxa_falha"]
                  else cor("[ON]    ","verde"))
        pri=f"[{c['prioridade']}]"
        print(f"  {_pad(pri,C_PRI)} {_pad(c['nome'],C_NOME)} "
              f"{_pad(c['banda'],C_BANDA)} {_pad(c['latencia'],C_LAT)} "
              f"{_pad(c['custo'],C_CUSTO)} {estado}")
    print(f"  {'─'*78}")
    print(f"\n  {cor('ℹ','azul')}  Em falha, o próximo canal na hierarquia assume automaticamente.")
    pausar()

def simular_transmissao():
    limpar_tela()
    titulo("","SIMULAR TRANSMISSÃO DE SOCORRO","Mostra como o sistema tenta cada canal até transmitir")
    dica("Preencha os dados da mensagem a ser enviada via rádio/satélite.")
    lat=ler_float("Latitude",-90,90); lon=ler_float("Longitude",-180,180)
    tipo=ler_texto("Tipo de emergência",exemplo="Soterrado"); urg=ler_int("Score de urgência",0,100)
    payload=f"LAT:{lat:.4f}|LON:{lon:.4f}|TIPO:{tipo[:20]}|URG:{urg}"
    print(f"\n  {cor('Payload:','cinza')} {cor(payload,'branco')}  {cor(f'({len(payload.encode())}B)','cinza')}")
    print(f"  {cor('Tentando canais em ordem de prioridade...','azul')}\n"); time.sleep(0.4)
    ok = False
    for c in CANAIS_COMM:
        pri2=f"[{c['prioridade']}]"
        print(f"  {cor(pri2,'cinza')} {c['nome']:<34}", end="", flush=True)
        time.sleep(0.6)
        if random.random() >= c["taxa_falha"]:
            print(cor(f"  OK  (latência: {c['latencia']})","verde"))
            log("Transmissão OK",f"{c['nome']} | {len(payload.encode())}B | URG:{urg}")
            print(f"\n  {cor('  Mensagem entregue via '+c['nome']+'!','verde')}")
            print(f"  {cor('  Confirmação em: '+c['latencia'],'cinza')}")
            ok = True; break
        print(cor("  FALHOU — tentando próximo...","vermelho"))
    if not ok:
        log("Transmissão falhou",f"Todos os canais indisponíveis | URG:{urg}")
        print(f"\n  {cor('[!!!] TODOS OS CANAIS FALHARAM.','vermelho')}")
        print(f"  {cor('  Mensagem salva localmente para reenvio automático.','laranja')}")
    pausar()

def simular_failover():
    limpar_tela()
    titulo("","SIMULAÇÃO DE FALHA EM CASCATA","Observe o sistema mantendo comunicação mesmo com canais caindo")
    dica("Cenário: desastre destrói infraestrutura progressivamente.")
    estados=[True]*len(CANAIS_COMM)
    def mostrar():
        for i,c in enumerate(CANAIS_COMM):
            st=cor("[ON]    ","verde") if estados[i] else cor("[OFF]   ","vermelho")
            pri3=f"[{c['prioridade']}]"
            print(f"    {cor(pri3,'cinza')} {c['nome']:<35} {st}")
    print(f"\n  {cor('Estado inicial (antes do desastre):','bold')}"); mostrar()
    for fase,desc,idx in [
        ("Fase 1","Torres de celular caem — 4G/5G comprometido",2),
        ("Fase 2","Repetidoras LoRa danificadas pela inundação",1),
        ("Fase 3","WiFi local perdido — energia cortada",4),
    ]:
        print(f"\n  {cor(f'▶ {fase}:','laranja')} {desc}..."); time.sleep(1.2)
        estados[idx]=False; mostrar()
    ativos=[CANAIS_COMM[i] for i,ok in enumerate(estados) if ok]
    print(f"\n  {cor('Failover automático ativado.','azul')} {len(ativos)} canal(is) sobrevivente(s):")
    for c in ativos: print(f"    {cor('','verde')}  {c['nome']} — operando como canal principal")
    print(f"\n  {cor('DisasterLink manteve conectividade sem intervenção humana.','verde')}")
    log("Simulação failover",f"{len(ativos)} canais sobreviventes")
    pausar()

def calcular_custo_transmissao():
    limpar_tela()
    titulo("","CALCULADORA DE CUSTO DE OPERAÇÃO","Compare custo do satélite Iridium vs alternativas gratuitas")
    msgs=ler_int("Mensagens estimadas por dia",1,100_000)
    dias=ler_int("Período em dias",1,365)
    cambio=ler_float("Cotação USD → BRL",1.0,20.0)
    total=msgs*dias; usd=total*0.04; brl=usd*cambio; g4=(dias/30)*35
    print(f"\n  {cor('═'*51,'azul')}")
    print(f"  {cor('  RESULTADO DA ESTIMATIVA','bold')}")
    print(f"  {cor('─'*51,'azul')}")
    print(f"    Total de mensagens Iridium:  {total:>12,}")
    print(f"    Custo Iridium SBD:           US$ {usd:>8,.2f}")
    print(f"    Equivalente em BRL:          R$  {brl:>8,.2f}")
    print(f"    Custo 4G estimado:           R$  {g4:>8,.2f}")
    print(f"    Canais gratuitos:  LoRa Mesh, WiFi, HF Rádio")
    print(f"  {cor('═'*51,'azul')}")
    print(f"\n  {cor(' Recomendação:','verde')} Priorize LoRa e HF para reduzir uso do Iridium.")
    pausar()

def comparativo_canais():
    limpar_tela()
    titulo("","COMPARATIVO TÉCNICO DOS CANAIS","Especificações e confiabilidade em cenários de desastre")
    C_NOME,C_BANDA,C_LAT,C_CUSTO = 26,16,9,16
    print(f"\n  {_pad(cor('Canal','cinza'),C_NOME)} {_pad(cor('Banda','cinza'),C_BANDA)} "
          f"{_pad(cor('Latência','cinza'),C_LAT)} {_pad(cor('Custo','cinza'),C_CUSTO)} {cor('Confiabilidade','cinza')}")
    print(f"  {'─'*78}")
    for c in CANAIS_COMM:
        conf=100-int(c["taxa_falha"]*100)
        cb=cor("█"*(conf//10),"verde" if conf>=75 else "laranja")
        print(f"  {_pad(c['nome'],C_NOME)} {_pad(c['banda'],C_BANDA)} "
              f"{_pad(c['latencia'],C_LAT)} {_pad(c['custo'],C_CUSTO)} {cb} {conf}%")
    print(f"  {'─'*78}")
    pausar()

ESPECIALIDADES = [
    "Busca e Resgate Terrestre","Atendimento Médico de Emergência",
    "Combate a Incêndio / USAR","Mergulho / Resgate Aquático","Resgate em Altura / Montanha",
]

def menu_equipes_rotas():
    while True:
        limpar_tela(); cabecalho()
        titulo("","MÓDULO 3 — EQUIPES DE RESGATE E OTIMIZAÇÃO DE ROTAS","Cadastro, designação e acompanhamento de equipes")
        total=len(equipes); disp=sum(1 for e in equipes if e["status"]=="Disponível")
        aguard=sum(1 for v in vitimas if v["status"]=="Aguardando resgate")
        print(f"  {cor('─'*74,'cinza')}")
        print(f"  Total: {cor(str(total),'branco')}    Disponíveis: {cor(str(disp),'verde')}"
              f"    Em campo: {cor(str(total-disp),'laranja')}    Aguardando vítimas: {cor(str(aguard),'vermelho')}")
        print(f"  {cor('─'*74,'cinza')}\n")
        opcao("1","Cadastrar equipe",       " registrar nova equipe de resgate")
        opcao("2","Listar equipes",         " ver todas as equipes e seus status")
        opcao("3","Designar equipes",       " alocar equipes a vítimas automaticamente")
        opcao("4","Liberar equipe de missão"," marcar missão concluída, equipe disponível")
        opcao("5","Relatório de campo",     " visão completa de equipes em campo")
        print(); opcao("0","Voltar ao menu principal",cor_tecla="cinza")
        rodape("A designação otimizada prioriza vítimas críticas + menor distância da equipe.")
        match ler_opcao(["1","2","3","4","5","0"]):
            case "1": cadastrar_equipe()
            case "2": listar_equipes()
            case "3": designar_equipe()
            case "4": liberar_equipe()
            case "5": relatorio_equipes()
            case "0": break

def cadastrar_equipe():
    limpar_tela()
    titulo("","CADASTRAR EQUIPE DE RESGATE","Registre uma nova equipe disponível para missões")
    id_e=f"EQ{len(equipes)+1:03d}"
    print(f"  {cor('ID gerado:','cinza')} {cor(id_e,'ciano')}\n")
    nome=ler_texto("Nome da equipe",exemplo="Bombeiros")
    secao("Especialidade")
    for i,e in enumerate(ESPECIALIDADES,1): print(f"  {cor(f'[{i}]','ciano')}  {e}")
    idx=ler_int("Especialidade",1,5)
    membros=ler_int("Número de membros",1,20)
    vel=ler_float("Velocidade média de deslocamento (km/h)",10,120)
    secao("Localização Atual da Equipe")
    print(f"  {cor('Exemplo SP:','cinza')} lat -23.5505, lon -46.6333")
    lat=ler_float("Latitude",-90,90); lon=ler_float("Longitude",-180,180)
    equipes.append({"id":id_e,"nome":nome,"especialidade":ESPECIALIDADES[idx-1],
        "membros":membros,"velocidade_kmh":vel,"lat":lat,"lon":lon,"status":"Disponível",
        "vitima_designada":None,"cadastrado_em":datetime.datetime.now().strftime("%d/%m/%Y %H:%M")})
    log("Equipe cadastrada",f"{id_e} — {nome}")
    sucesso(f"Equipe {id_e} — {nome} cadastrada com sucesso!")
    dica("Use a opção [3] Designar equipes para alocar esta equipe a uma vítima.")
    pausar()

def listar_equipes():
    limpar_tela()
    titulo("","EQUIPES DE RESGATE CADASTRADAS","Lista completa com status e atribuições")
    if not equipes: aviso("Nenhuma equipe cadastrada."); pausar(); return
    C_ID,C_NOME,C_ESP,C_MBR = 7,22,34,4
    print(f"  {_pad(cor('ID','cinza'),C_ID)} {_pad(cor('Nome','cinza'),C_NOME)} "
          f"{_pad(cor('Especialidade','cinza'),C_ESP)} {cor('Mbr','cinza').rjust(C_MBR)}  "
          f"{_pad(cor('Status','cinza'),12)}  {cor('Vítima','cinza')}")
    print(f"  {'─'*78}")
    for e in equipes:
        sc="verde" if e["status"]=="Disponível" else "laranja"
        print(f"  {_pad(cor(e['id'],'ciano'),C_ID)} {_pad(e['nome'][:C_NOME],C_NOME)} "
              f"{_pad(e['especialidade'][:C_ESP],C_ESP)} {str(e['membros']).rjust(C_MBR)}  "
              f"{_pad(cor(e['status'],sc),22)}  {e['vitima_designada'] or '—'}")
    print(f"  {'─'*78}")
    disp=sum(1 for e in equipes if e["status"]=="Disponível")
    print(f"\n  Total: {cor(str(len(equipes)),'branco')}    Disponíveis: {cor(str(disp),'verde')}"
          f"    Em missão: {cor(str(len(equipes)-disp),'laranja')}")
    pausar()

def designar_equipe():
    limpar_tela()
    titulo("","DESIGNAR EQUIPES — OTIMIZAÇÃO AUTOMÁTICA","Critério: maior urgência + menor distância da equipe")
    vit_ag=[v for v in vitimas if v["status"]=="Aguardando resgate"]
    eq_di =[e for e in equipes if e["status"]=="Disponível"]
    if not vit_ag: aviso("Nenhuma vítima aguardando resgate no momento."); pausar(); return
    if not eq_di:  aviso("Nenhuma equipe disponível."); pausar(); return
    print(f"\n   Vítimas aguardando: {cor(str(len(vit_ag)),'vermelho')}   "
          f" Equipes disponíveis: {cor(str(len(eq_di)),'verde')}")
    print(f"\n  {cor('Calculando designações ótimas...','azul')}"); time.sleep(0.8)
    atrib=[]; vr=sorted(vit_ag,key=lambda v:v["score"],reverse=True); er=list(eq_di)
    for v in vr:
        if not er: break
        me=min(er,key=lambda e:distancia(v["lat"],v["lon"],e["lat"],e["lon"]))
        d=distancia(v["lat"],v["lon"],me["lat"],me["lon"]); eta=calc_eta(d,me["velocidade_kmh"])
        me["status"]="Em missão"; me["vitima_designada"]=v["id"]
        v["status"]="Equipe a caminho"; v["atualizado_em"]=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        atrib.append((me,v,d,eta)); er.remove(me)
        log("Designação",f"{me['id']} → {v['id']} ({d:.1f} km | ETA {eta})")
    C_EQ,C_VIT,C_DIST,C_ETA,C_SC = 22,22,10,8,6
    print(f"\n  {_pad(cor('Equipe','cinza'),C_EQ)}    {_pad(cor('Vítima','cinza'),C_VIT)}  "
          f"{_pad(cor('Dist.','cinza'),C_DIST)}  {_pad(cor('ETA','cinza'),C_ETA)}  {cor('Score','cinza')}")
    print(f"  {'─'*78}")
    for e,v,d,et in atrib:
        nc=urgencia_cor(v["score"])
        print(f"  {_pad(cor(e['nome'][:C_EQ],'ciano'),C_EQ)}    {_pad(v['nome'][:C_VIT],C_VIT)}  "
              f"{_pad(f'{d:.1f} km',C_DIST)}  {_pad(cor(et,'verde'),C_ETA+9)}  "
              f"{cor(str(v['score']).rjust(C_SC),nc)}")
    print(f"  {'─'*78}")
    sem=len(vr)-len(atrib)
    if sem>0: aviso(f"{sem} vítima(s) sem equipe — cadastre mais equipes (opção [1]).")
    sucesso(f"{len(atrib)} designação(ões) realizada(s) com sucesso!")
    pausar()

def liberar_equipe():
    limpar_tela()
    titulo("","LIBERAR EQUIPE DE MISSÃO","Registre missão concluída e torne a equipe disponível")
    em_m=[e for e in equipes if e["status"]=="Em missão"]
    if not em_m: aviso("Nenhuma equipe em missão no momento."); pausar(); return
    print(f"  {cor('Equipes atualmente em campo:','bold')}\n")
    for i,e in enumerate(em_m,1):
        print(f"  {cor(f'[{i}]','ciano')}  {e['id']} — {e['nome']:<22} {cor('Vítima:','cinza')} {e['vitima_designada']}")
    eq=em_m[ler_int("Escolha a equipe a liberar",1,len(em_m))-1]
    eq["status"]="Disponível"; eq["vitima_designada"]=None
    log("Equipe liberada",f"{eq['id']} — {eq['nome']}")
    sucesso(f"{eq['nome']} está disponível novamente para nova missão.")
    pausar()

def relatorio_equipes():
    limpar_tela()
    titulo("","RELATÓRIO DE EQUIPES — CAMPO E BASE","Visão completa de todas as equipes e suas atribuições")
    em_m=[e for e in equipes if e["status"]=="Em missão"]
    disp=[e for e in equipes if e["status"]=="Disponível"]
    print(f"\n  Total: {cor(str(len(equipes)),'branco')}    Em missão: {cor(str(len(em_m)),'laranja')}"
          f"    Disponíveis: {cor(str(len(disp)),'verde')}")
    if em_m:
        secao("Equipes em Campo")
        for e in em_m:
            vi=next((v for v in vitimas if v["id"]==e.get("vitima_designada")),None)
            d=distancia(vi["lat"],vi["lon"],e["lat"],e["lon"]) if vi else 0
            et=calc_eta(d,e["velocidade_kmh"]) if vi else "?"
            nc=urgencia_cor(vi["score"]) if vi else "cinza"
            print(f"  {cor(e['id'],'ciano')} — {cor(e['nome'],'bold')}")
            print(f"    Vítima: {e['vitima_designada']} ({vi['nome'] if vi else '?'})  "
                  f"│  Score: {cor(str(vi['score'] if vi else 0),nc)}")
            print(f"    Distância: {d:.1f} km  │  ETA: {cor(et,'verde')}")
            print(f"  {'·'*40}")
    if disp:
        secao("Equipes Disponíveis")
        for e in disp:
            esp_txt=f"({e['especialidade']})"
            print(f"  {cor(e['id'],'ciano')} — {e['nome']:<22} {cor(esp_txt,'cinza')}  │  {e['membros']} membros")
    pausar()

def _barra_progresso(label, passos=20, delay=0.07):
    print(f"\n  {cor(label,'cinza')}")
    for i in range(passos+1):
        pct=int((i/passos)*100)
        print(f"\r  [{cor('█'*i,'ciano')}{cor('░'*(passos-i),'cinza')}] {cor(f'{pct:3d}%','bold')}", end="", flush=True)
        time.sleep(delay)
    print()

def menu_deteccao_passiva():
    while True:
        limpar_tela(); cabecalho()
        titulo("","MÓDULO 4 — SIMULADOR DE DETECÇÃO PASSIVA","Sensores para localizar vítimas sem comunicação ativa")
        opcao("1","Câmera Térmica (IR)",   " detecta gradiente de calor humano sob escombros")
        opcao("2","Escuta Acústica (MEMS)"," analisa sons de voz em profundidades")
        opcao("3","Radar UWB Respiratório"," detecta movimento do peito através de paredes")
        opcao("4","Rastreamento BLE/WiFi", " triangulação passiva pelo celular da vítima")
        opcao("5","Varredura Combinada",   " fusão de 4 sensores para máxima confiança")
        print(); opcao("0","Voltar ao menu principal",cor_tecla="cinza")
        rodape("Varredura combinada [5] dá muito mais confiança do que sensores isolados.")
        match ler_opcao(["1","2","3","4","5","0"]):
            case "1": simular_termico()
            case "2": simular_acustico()
            case "3": simular_uwb()
            case "4": simular_ble_wifi()
            case "5": varredura_combinada()
            case "0": break

def simular_termico(area=None):
    standalone = area is None
    if standalone:
        limpar_tela()
        titulo("","CÂMERA TÉRMICA — FLIR Lepton 3.5","Detecta gradiente 36–37°C (corpo humano). Alcance: até 30cm de entulho")
        area=ler_int("Área a varrer (m²)",100,5_000)
    _barra_progresso("Processando frames térmicos FLIR Lepton 3.5...",20,0.05)
    n=random.randint(0,max(1,area//200))
    print(f"\n  {cor('  Análise concluída.','bold')} {n} ponto(s) com gradiente 36–37 °C:\n")
    for i in range(n):
        x=random.uniform(0,math.sqrt(area)); y=random.uniform(0,math.sqrt(area))
        temp=round(random.uniform(35.5,37.8),1)
        tipo=random.choice([cor("Silhueta humana confirmada ","verde"),
                            cor("Possível humano — revisar ","laranja"),
                            cor("Animal descartado ","cinza")])
        print(f"  Ponto {i+1:>2}: ({x:.1f}m, {y:.1f}m) │ {temp}°C │ {tipo}")
    if n>0: print(f"\n  {cor('','azul')} Recomendação: acionar Módulo 1 para registrar vítimas detectadas.")
    log("Varredura térmica",f"Área: {area}m² | Detectados: {n}")
    if standalone: pausar()
    return n

def simular_acustico(profundidade=None):
    standalone = profundidade is None
    if standalone:
        limpar_tela()
        titulo("","ESCUTA ACÚSTICA — ARRAY MEMS","Detecta voz, choro e batidas. Maior profundidade = menor chance")
        profundidade=ler_int("Profundidade do entulho (m)",0,15)
    _barra_progresso("Beamforming e filtragem espectral (80–3000 Hz)...",18,0.06)
    detectou=random.random() < max(0.1,1.0-profundidade*0.06)
    print(f"\n  {cor('  Análise concluída.','bold')} Ruído filtrado: maquinário, vento, multidão.")
    if detectou:
        ang=random.randint(0,359); dist=random.uniform(1.0,max(1.0,15-profundidade*0.8))
        freq=random.uniform(150,800)
        print(f"\n  {cor('  VOZ HUMANA DETECTADA!','verde')}")
        print(f"  Direção: {ang}°  │  Distância est.: {dist:.1f}m  │  Freq.: {freq:.0f} Hz")
        log("Detecção acústica",f"Ângulo:{ang}° | Dist:{dist:.1f}m")
    else:
        aviso("Sem padrão vocal detectado nessa profundidade.")
        dica("Tente radar UWB [3] para profundidades maiores.")
    if standalone: pausar()
    return detectou

def simular_uwb(material=None, espessura=None):
    standalone = material is None
    if standalone:
        limpar_tela()
        titulo("","RADAR UWB RESPIRATÓRIO — XeThru X4","Detecta movimento do peito de 0.3mm através de concreto/tijolo/madeira")
        print(f"  Materiais: {cor('tijolo','ciano')}, {cor('concreto','ciano')}, {cor('madeira','ciano')}")
        print(f"\n  {cor('▶','ciano')} Material do entulho {cor('(ENTER = concreto)','cinza')}: ", end="")
        material=input("").strip().lower() or "concreto"
        espessura=ler_int("Espessura (cm)",0,100)
    fator={"concreto":0.85,"tijolo":0.60,"madeira":0.40}.get(material,0.65)
    alcance=max(0.0,30.0-(espessura or 0)*fator)
    _barra_progresso("Emitindo pulsos UWB 6–9 GHz e analisando fase refletida...",15,0.08)
    detectou=alcance>5 and random.random()<0.75
    print(f"\n  {cor('Alcance efetivo neste cenário:','bold')} {alcance:.1f} cm")
    if detectou:
        fr=round(random.uniform(8,22),1)
        normal=12<=fr<=20
        print(f"\n  {cor('  RESPIRAÇÃO DETECTADA!','verde')}")
        print(f"  Frequência: {fr} resp/min  │  {cor('Normal','verde') if normal else cor('Fora do padrão','laranja')}")
        log("Detecção UWB",f"Respiração: {fr} resp/min | Material: {material}")
    else:
        erro("Sinal insuficiente. Mude o ponto de varredura ou reduza a distância.")
    if standalone: pausar()
    return detectou

def simular_ble_wifi(n_kits=None):
    standalone = n_kits is None
    if standalone:
        limpar_tela()
        titulo("","RASTREAMENTO PASSIVO BLE/WiFi — TRIANGULAÇÃO RSSI","Detecta o celular da vítima sem ela fazer nada. Precisa de 3 kits")
        n_kits=ler_int("Número de kits DisasterLink na área",1,5)
    print(f"\n  {cor('Escaneando probe requests WiFi e beacons BLE...','cinza')}\n")
    _barra_progresso("Coletando RSSI dos kits vizinhos...",12,0.07)
    n=random.randint(0,8)
    print(f"\n  {cor('  '+str(n)+' dispositivo(s) detectado(s):','bold')}\n")
    for i in range(n):
        mac=":".join(f"{random.randint(0,255):02X}" for _ in range(6))
        rssi=[random.randint(-90,-30) for _ in range(min(n_kits,3))]
        prec="±3m" if n_kits>=3 else cor("±15m (precisão baixa — adicione mais kits)","laranja")
        lat_e=round(random.uniform(-23.6,-23.4),5); lon_e=round(random.uniform(-46.8,-46.5),5)
        print(f"  {cor(f'[{i+1}]','ciano')} MAC: {mac}  │  RSSI: {rssi} dBm")
        print(f"       Posição est.: ({lat_e}, {lon_e})  │  Precisão: {prec}")
    if n==0: aviso("Nenhum sinal BLE/WiFi detectado.")
    log("Varredura BLE/WiFi",f"Dispositivos: {n} | Kits: {n_kits}")
    if standalone: pausar()
    return n

def varredura_combinada():
    limpar_tela()
    titulo("","VARREDURA COMBINADA — 4 SENSORES SIMULTÂNEOS","A fusão de sensores aumenta muito a confiança na detecção")
    area=ler_int("Área de varredura (m²)",100,5_000)
    prof=ler_int("Profundidade do entulho (m)",0,15)
    print(f"\n  {cor('▶','ciano')} Material para UWB {cor('[tijolo/concreto/madeira]','cinza')}: ", end="")
    mat=input("").strip().lower() or "concreto"
    esp=ler_int("Espessura do entulho para UWB (cm)",0,100)
    n_kits=ler_int("Kits DisasterLink na área",1,5)
    print(f"\n{cor('═'*78,'azul')}")
    print(cor("   INICIANDO VARREDURA COMBINADA — 4 SENSORES","bold"))
    print(f"{cor('═'*78,'azul')}")
    nt=simular_termico(area); da=simular_acustico(prof)
    du=simular_uwb(mat,esp);  nb=simular_ble_wifi(n_kits)
    ev=sum([nt>0,da,du,nb>0])
    confs=[cor("Nenhuma evidência","cinza"),cor("Baixa   (1/4 sensores)","laranja"),
           cor("Média   (2/4 sensores)","laranja"),cor("Alta    (3/4 sensores)","verde"),
           cor("Muito Alta (4/4 sensores)","verde")]
    print(f"\n{cor('═'*78,'azul')}")
    print(cor("  RESULTADO CONSOLIDADO","bold"))
    print(f"{cor('═'*78,'azul')}")
    print(f"  Sensor térmico  : {cor(f'{nt} ponto(s)','verde' if nt>0 else 'cinza')}")
    print(f"  Sensor acústico : {cor('Voz detectada','verde') if da else cor('Sem detecção','cinza')}")
    print(f"  Radar UWB       : {cor('Respiração','verde') if du else cor('Sem detecção','cinza')}")
    print(f"  BLE/WiFi        : {cor(f'{nb} dispositivo(s)','verde' if nb>0 else 'cinza')}")
    print(f"  Confiança geral : {confs[ev]}")
    if ev>=2:
        alerta_critico("PRESENÇA HUMANA CONFIRMADA — acionar equipe de resgate!")
        print(f"  {cor(' Módulo 1 para registrar a vítima, Módulo 3 para enviar equipe.','azul')}")
    else:
        aviso("Evidências insuficientes. Ampliar varredura ou mudar posição.")
    log("Varredura combinada",f"Evidências: {ev}/4")
    pausar()

def menu_painel():
    while True:
        limpar_tela(); cabecalho()
        titulo("","MÓDULO 5 — PAINEL DE CONTROLE E RELATÓRIOS","Métricas, estatísticas, mapa e exportação de dados")
        opcao("1","Dashboard geral",          " visão consolidada de vítimas e equipes")
        opcao("2","Relatório por status",     " vítimas agrupadas por estado de resgate")
        opcao("3","Estatísticas de triagem",  " distribuição de urgência, canais e tipos")
        opcao("4","Mapa de calor (ASCII)",    " distribuição geográfica por urgência")
        opcao("5","Log de execução",          " histórico de ações do sistema")
        opcao("6","Exportar dados para JSON", " salvar todos os dados em arquivo")
        print(); opcao("0","Voltar ao menu principal",cor_tecla="cinza")
        rodape()
        match ler_opcao(["1","2","3","4","5","6","0"]):
            case "1": dashboard_geral()
            case "2": relatorio_vitimas_status()
            case "3": estatisticas_triagem()
            case "4": mapa_calor_urgencia()
            case "5": exibir_log()
            case "6": exportar_json()
            case "0": break

def dashboard_geral():
    limpar_tela()
    titulo("","DASHBOARD GERAL — DisasterLink","Visão consolidada em tempo real")
    criticos=sum(1 for v in vitimas if v["score"]>=85)
    altos   =sum(1 for v in vitimas if 60<=v["score"]<85)
    medios  =sum(1 for v in vitimas if 35<=v["score"]<60)
    baixos  =sum(1 for v in vitimas if v["score"]<35)
    res     =sum(1 for v in vitimas if v["status"]=="Resgatado")
    eq_disp =sum(1 for e in equipes if e["status"]=="Disponível")
    eq_miss =sum(1 for e in equipes if e["status"]=="Em missão")
    COL=30; div="  "+"─"*(COL*2+5)
    def row(le,ve,ld="",vd=""):
        esq=_pad(f"  {le} {ve}",COL); dir=_pad(f"  {ld} {vd}",COL) if ld else " "*COL
        return f"  {esq}  {dir}"
    print(f"\n  {cor('Atualizado em:','cinza')} {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    print(div); print(f"  {_pad('  VÍTIMAS REGISTRADAS',COL)}  {_pad('  EQUIPES',COL)}"); print(div)
    print(row("Total            :",len(vitimas),  "Total            :",len(equipes)))
    print(row(" Críticas      :",criticos,         " Disponíveis   :",eq_disp))
    print(row(" Alta urgência :",altos,            " Em missão     :",eq_miss))
    print(row(" Média urgência:",medios,           " Logs sessão   :",len(logs)))
    print(row(" Baixa         :",baixos)); print(row(" Resgatadas    :",res)); print(div)
    if vitimas:
        media=sum(v["score"] for v in vitimas)/len(vitimas)
        print(f"\n  {cor('Score médio de triagem:','cinza')} {cor(f'{media:.1f}/100','bold')}  {barra(int(media))}")
    if not vitimas and not equipes:
        print(f"\n  {cor('ℹ  Sistema vazio.','azul')} Carregue dados demo ou use os módulos 1 e 3.")
    pausar()

def relatorio_vitimas_status():
    limpar_tela()
    titulo("","RELATÓRIO DE VÍTIMAS POR STATUS","Vítimas agrupadas pelo seu estado atual de resgate")
    if not vitimas: aviso("Nenhuma vítima registrada."); pausar(); return
    sd: dict[str,list] = {}
    for v in vitimas: sd.setdefault(v["status"],[]).append(v)
    for st in STATUS_VITIMA:
        lista=sd.get(st,[])
        if not lista: continue
        secao(f"{st}  ({len(lista)} vítima(s))")
        for v in sorted(lista,key=lambda x:x["score"],reverse=True):
            nc=urgencia_cor(v["score"])
            print(f"  {cor(v['id'],'ciano')}  │  {v['nome'][:25]:<25}  │  "
                  f"Score: {cor(str(v['score']),nc):>3}  │  {cor(v['nivel'],nc)}")
    pausar()

def estatisticas_triagem():
    limpar_tela()
    titulo("","ESTATÍSTICAS DE TRIAGEM","Distribuição por urgência, canal de detecção e tipo de emergência")
    if not vitimas: aviso("Nenhuma vítima registrada."); pausar(); return
    scores=[v["score"] for v in vitimas]; media=sum(scores)/len(scores)
    dp=(sum((s-media)**2 for s in scores)/len(scores))**0.5
    print(f"\n  {cor('Total de vítimas:','cinza')}  {cor(str(len(vitimas)),'branco')}")
    print(f"  {cor('Score médio:','cinza')}       {media:.1f}  {barra(int(media))}")
    print(f"  {cor('Score máximo:','cinza')}      {max(scores)}")
    print(f"  {cor('Score mínimo:','cinza')}      {min(scores)}")
    print(f"  {cor('Desvio padrão:','cinza')}     {dp:.1f}")
    secao("Distribuição por Nível de Urgência")
    for label,low,high,c in [("[!!!] CRITICO",85,101,"vermelho"),("[ !! ] ALTO  ",60,85,"laranja"),
                               ("[  ! ] MEDIO ",35,60,"laranja"),("[    ] BAIXO ",0,35,"verde")]:
        qtd=sum(1 for s in scores if low<=s<high)
        print(f"  {label:<20} {cor('█'*qtd,c)} ({qtd})")
    secao("Canal de Detecção")
    cnt: dict[str,int]={}
    for v in vitimas: cnt[v["canal"]]=cnt.get(v["canal"],0)+1
    for canal,qtd in sorted(cnt.items(),key=lambda x:-x[1]):
        print(f"  {canal[:38]:<38} {cor('█'*qtd,'ciano')} ({qtd})")
    secao("Tipo de Emergência")
    cnt={}
    for v in vitimas: cnt[v["tipo_desc"]]=cnt.get(v["tipo_desc"],0)+1
    for tipo,qtd in sorted(cnt.items(),key=lambda x:-x[1]):
        print(f"  {tipo[:38]:<38} {cor('█'*qtd,'ciano')} ({qtd})")
    pausar()

def mapa_calor_urgencia():
    limpar_tela()
    titulo("","MAPA DE CALOR — DISTRIBUIÇÃO GEOGRÁFICA","Posicionamento das vítimas por urgência no mapa ASCII")
    if not vitimas: aviso("Nenhuma vítima registrada."); pausar(); return
    LINHAS, COLS = 18, 56
    grade = [[" " for _ in range(COLS)] for _ in range(LINHAS)]
    lats=[v["lat"] for v in vitimas]; lons=[v["lon"] for v in vitimas]
    lat_min=min(lats)-0.001; lat_max=max(lats)+0.001
    lon_min=min(lons)-0.001; lon_max=max(lons)+0.001
    for v in vitimas:
        col=int((v["lon"]-lon_min)/(lon_max-lon_min)*(COLS-1))
        lin=int((lat_max-v["lat"])/(lat_max-lat_min)*(LINHAS-1))
        col=max(0,min(COLS-1,col)); lin=max(0,min(LINHAS-1,lin))
        simbolo,c=(
            ("●","vermelho") if v["score"]>=85 else
            ("◆","laranja")  if v["score"]>=60 else
            ("▲","azul")     if v["score"]>=35 else
            ("·","cinza")
        )
        grade[lin][col]=cor(simbolo,c)
    print(f"\n  {cor('Legenda:','cinza')} "
          f"{cor('● Crítico','vermelho')}  {cor('◆ Alto','laranja')}  "
          f"{cor('▲ Médio','azul')}  {cor('· Baixo','cinza')}\n")
    lat_n = f"{lat_max:.4f}"; lat_s = f"{lat_min:.4f}"
    lon_w = f"{lon_min:.4f}"; lon_e = f"{lon_max:.4f}"
    PAD = 10
    print(f"  {cor(lat_n.rjust(PAD),'cinza')} ┌{'─'*COLS}┐")
    for row in grade:
        print(f"  {' '*PAD} │{''.join(row)}│")
    print(f"  {cor(lat_s.rjust(PAD),'cinza')} └{'─'*COLS}┘")
    offset = PAD + 2; gap = COLS - len(lon_w) - len(lon_e)
    print(f"  {' '*offset}{cor(lon_w,'cinza')}{' '*gap}{cor(lon_e,'cinza')}")
    print(f"\n  {cor('Vítimas plotadas:','cinza')} {cor(str(len(vitimas)),'branco')}"
          f"   {cor('Área:','cinza')} lat [{lat_s} → {lat_n}]  lon [{lon_w} → {lon_e}]")
    pausar()

def exibir_log():
    limpar_tela()
    titulo("","LOG DE EXECUÇÃO DO SISTEMA","Histórico das últimas 50 ações realizadas nesta sessão")
    if not logs: aviso("Nenhuma entrada de log ainda."); pausar(); return
    print(f"\n  {cor('Hora','cinza'):<12} {cor('Ação','cinza'):<34} {cor('Detalhe','cinza')}")
    print(f"  {'─'*74}")
    for e in logs[-50:]:
        print(f"  {cor(e['hora'],'ciano'):<12} {e['acao'][:32]:<34} {cor(e['detalhe'][:40],'cinza')}")
    if len(logs)>50: print(f"\n  {cor(f'... exibindo últimas 50 de {len(logs)} entradas.','cinza')}")
    pausar()

def exportar_json():
    limpar_tela()
    titulo("","EXPORTAR DADOS PARA JSON","Salva todos os dados do sistema em arquivo para análise externa")
    dica("O arquivo JSON pode ser usado em análise de dados ou integração com outros sistemas.")
    nome_sug = f"disasterlink_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\n  {cor('Nome sugerido:','cinza')} {cor(nome_sug,'ciano')}")
    print(f"  {cor('▶','ciano')} Nome do arquivo {cor('(ENTER para usar o sugerido)','cinza')}: ", end="")
    nome = input("").strip() or nome_sug
    if not nome.endswith(".json"): nome += ".json"
    nome_seguro = _re.sub(r'[\\/*?:"<>|]', "_", nome)
    caminho = os.path.join(os.getcwd(), nome_seguro)
    dados = {
        "exportado_em": datetime.datetime.now().isoformat(),
        "versao": "DisasterLink — FIAP Global Solution 2026",
        "resumo": {
            "total_vitimas": len(vitimas), "total_equipes": len(equipes),
            "total_logs": len(logs),       "total_ocorrencias": len(ocorrencias),
        },
        "vitimas": vitimas, "equipes": equipes,
        "ocorrencias": ocorrencias, "logs": logs,
    }
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        sucesso(f"Dados exportados com sucesso!")
        print(f"\n  {cor('Arquivo:','cinza')}      {cor(caminho,'branco')}")
        print(f"  {cor('Vítimas:','cinza')}      {len(vitimas)}")
        print(f"  {cor('Equipes:','cinza')}      {len(equipes)}")
        print(f"  {cor('Ocorrências:','cinza')}  {len(ocorrencias)}")
        print(f"  {cor('Logs:','cinza')}         {len(logs)}")
        log("Exportação JSON", caminho)
    except OSError as e:
        erro(f"Falha ao exportar: {e}")
        dica("Verifique se o diretório tem permissão de escrita e tente novamente.")
    pausar()

def menu_principal():
    log("Sistema iniciado","DisasterLink")
    while True:
        limpar_tela(); print()
        print(cor("  "+"═"*76,"azul"))
        print("  "+cor("    DISASTERLINK","bold")+cor("  —  Plataforma de Resposta a Emergências","branco"))
        print("  "+cor("      FIAP Global Solution 2026  ·  Space Connect","cinza"))
        print(cor("  "+"═"*76,"azul"))
        criticos=sum(1 for v in vitimas if v["score"]>=85 and v["status"]=="Aguardando resgate")
        eq_disp =sum(1 for e in equipes if e["status"]=="Disponível")
        print()
        print(f"  Vítimas: {cor(str(len(vitimas)),'branco')}    "
              f"Críticas: {cor(str(criticos),'vermelho' if criticos>0 else 'cinza')}    "
              f"Equipes disponíveis: {cor(str(eq_disp),'verde')}    "
              f"Logs: {cor(str(len(logs)),'cinza')}")
        print(); print(cor("  "+"─"*74,"cinza")); print()
        opcao("1","  Registro e Triagem de Vítimas",   "cadastrar, listar, atualizar")
        opcao("2","  Simulador de Comunicação",         "canais, failover, custo")
        opcao("3","  Equipes de Resgate e Rotas",       "designar, liberar, relatório")
        opcao("4","  Simulador de Detecção Passiva",    "térmico, acústico, radar, BLE")
        opcao("5","  Painel de Controle e Relatórios",  "dashboard, mapa, exportar")
        print()
        opcao("D","  Carregar Dados de Demonstração",   "cenário pré-configurado para testes",cor_tecla="verde")
        print()
        print(f"  {cor('[0]','cinza')}     Sair do sistema")
        print(); print(cor("  "+"─"*74,"cinza"))
        if criticos>0:
            print(f"\n  {cor(f'  {criticos} vítima(s) CRÍTICA(S) aguardando resgate!  → Módulo 3','vermelho')}")
        elif not vitimas:
            print(f"\n  {cor('ℹ  Sistema vazio. Use [D] para carregar dados de demonstração.','azul')}")
        print()
        match ler_opcao(["1","2","3","4","5","D","0"]):
            case "1": menu_registro_vitimas()
            case "2": menu_simulador_comunicacao()
            case "3": menu_equipes_rotas()
            case "4": menu_deteccao_passiva()
            case "5": menu_painel()
            case "D": carregar_dados_demo()
            case "0":
                log("Sistema encerrado")
                limpar_tela()
                print(f"\n  {cor('DisasterLink encerrado.','bold')}")
                print(f"  {cor('Nenhuma lacuna no resgate.','cinza')}\n")
                break

if __name__ == "__main__":
    menu_principal()
