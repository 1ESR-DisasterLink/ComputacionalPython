# 📊 DisasterLink 

> Projeto desenvolvido como parte da disciplina de Computational Thinking with Python.

---

## 📌 Descrição do projeto

Quando uma enchente, desabamento ou incêndio acontece, a infraestrutura de comunicação cai junto, sem celular, sem internet, sem luz. Vítimas não conseguem pedir socorro, equipes de resgate não sabem aonde ir e a Defesa Civil coordena ações às cegas. Isso aconteceu no Rio Grande do Sul em 2024, onde municípios inteiros ficaram dias sem comunicação.

O **DisasterLink** é um sistema de comunicação de emergência criado para resolver exatamente esse problema. A solução é composta por um kit físico portátil, um painel de comando para a Defesa Civil e um aplicativo para as equipes de resgate. O kit usa rádio LoRa para receber sinais de socorro das vítimas e envia as informações via 4G ou, quando este falha, via satélite Iridium, garantindo comunicação em qualquer lugar do planeta, independente de infraestrutura terrestre.

---

## 💬 Estrutura de navegação
 
- **Menu principal**: status em tempo real do sistema, com atalho [D] para carregar um cenário de demonstração pré-configurado.

- **Módulo 1 - Registro e triagem de vítimas**: cadastro de vítimas com score de urgência automático (0–100) calculado por tipo de emergência, horas sem resposta, vulnerabilidade e ferimentos.
  | Score | Nível |
  |-------|-------|
  | ≥ 85 | 🔴 CRÍTICO |
  | 60–84 | 🟠 ALTO |
  | 35–59 | 🟡 MÉDIO |
  | < 35 | 🟢 BAIXO |
  
- **Módulo 2 - Simulador de canais de comunicação**: hierarquia de canais com failover automático.
  | # | Canal | Latência | Custo | Confiab. |
  |---|-------|----------|-------|----------|
  | 1 | Satélite Iridium SBD | ~90s | US$ 0.04/msg | 95% |
  | 2 | Mesh LoRa | ~30s | Gratuito | 85% |
  | 3 | 4G/5G | ~2s | R$ 35/mês | 65% |
  | 4 | Rádio HF | ~5min | Gratuito | 75% |
  | 5 | WiFi Captive Portal | < 1s | Gratuito | 50% |
  
- **Módulo 3 - Equipes de resgate e rotas**: cadastro e despacho de equipes com designação otimizada com vítimas ordenadas por score, equipe mais próxima selecionada via fórmula de Haversine, ETA calculado pela velocidade da equipe. 

- **Módulo 4 - Simulador de detecção passiva**: simula sensores autônomos que detectam sobreviventes sem interação.
  | Sensor | Alcance | Uso |
  |--------|---------|-----|
  | Térmico / IR | 50 m | Noturno / fumaça |
  | Acústico | 20 m | Escombros |
  | Radar GPR | 3 m | Sub-superfície |
  | Bluetooth LE | 30 m | Beacon de celular |
  
- **Módulo 5 - Painel de controle e relatórios**: dashboard em tempo real, relatório estatístico (score médio, desvio padrão, distribuição por nível), mapa de calor ASCII geográfico e exportação completa para JSON.
---
 
## 🔧 Funcionalidades interativas
 
- Registrar, listar por urgência, atualizar status, pesquisar e exibir ficha completa de vítimas, com equipe designada e ETA.
- Simular transmissão, falha em cascata, custo de operação e comparativo técnico entre canais de comunicação.
- Designar e liberar equipes de resgate, com relatório de atividades.
- Simular detecção térmica, acústica, radar e Bluetooth LE, individualmente ou em varredura combinada.
- Dashboard e relatórios com estatísticas de triagem e mapa de calor de urgência.
- Exportação completa dos dados do sistema para JSON:
```json
{
  "exportado_em": "2026-06-02T14:35:00",
  "versao": "DisasterLink — FIAP Global Solution 2026",
  "resumo": { "total_vitimas": 5, "total_equipes": 3, "total_logs": 12 },
  "vitimas": [...],
  "equipes": [...],
  "logs": [...]
}
```
 
**Fluxo de uso:**
 
```
Desastre ocorre
      │
      ├── Portal WiFi (rede DISASTERLINK-AJUDA)
      └── Botão SOS físico (LoRa até 5 km)
            │
      Kit DisasterLink registra GPS + urgência
            │
      4G disponível? ──Sim──► Servidor Central
            │ Não
      Satélite Iridium (fallback automático)
            │
      Processamento Central
            ├── Dashboard Defesa Civil (mapa em tempo real)
            ├── Alertas WhatsApp (casos críticos < 1 min)
            └── App Equipe de Resgate (offline com rota)
                  │
            Vítima resgatada ✓
```
 
---
 
## 🛠️ Tecnologias utilizadas
 
| Tecnologia | Descrição |
|---|---|
| Python | Lógica do sistema, menus, simulações e cálculos (CLI em Python puro) |
| Git | Versionamento do projeto |
 
> Requer Python 3.10+ (uso de `match/case`). Compatível com Linux, macOS e Windows.
 
---
 
## ▶️ Como executar
 
```bash
# Clone o repositório
git clone https://github.com/1ESR-DisasterLink/ComputacionalPython.git
 
# Acesse a pasta
cd ComputacionalPython-main
 
# Execute o programa
python disasterlink.py
```
 
Ao iniciar, o menu principal exibe o status em tempo real: vítimas registradas, casos críticos, equipes disponíveis e log do sistema. Use [D] para carregar um cenário de demonstração pré-configurado.
 
---
 
## 📁 Estrutura do repositório
 
```
ComputacionalPython/
├── Disasterlink.py  ← Código fonte
└── README.md  ← Este arquivo
```

---

## 👩‍💻 Equipe

| Nome | RM |
|---|---|
| Caique Kenji Yafuco | 570368 |
| Guilherme Tome Nogueira | 570144 |
| Lucas de Andrade Astorini | 569119 |
| Sabrina Lopes da Silva | 571870 |
| Sofia Satomi Hagio | 569120 |
