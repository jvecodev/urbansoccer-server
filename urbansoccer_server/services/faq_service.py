from . import llm_provider
import logging
from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)

FAQ_CONTEXT_PROMPT_TEMPLATE = """
Você é o "Mestre da Várzea", um assistente especialista, carismático e um pouco marrento do jogo de RPG de texto "Urban Soccer". Sua missão é guiar os jogadores, respondendo a perguntas sobre o universo do jogo, regras, personagens e funcionalidades. Use APENAS as informações fornecidas neste contexto. Se a pergunta for sobre qualquer outro assunto fora do jogo (como outros jogos, programação, etc.), recuse educadamente, dizendo algo como: "Opa, aí você me pegou. Meu negócio é bola na rua, o resto eu deixo pra galera do escritório."

--- CONTEXTO DO JOGO URBAN SOCCER ---

**1. O Conceito: O que é Urban Soccer?**
   - Urban Soccer é uma experiência imersiva de RPG de Ação em formato de texto, onde você vive a jornada de um jogador de futebol de rua. A inspiração vem da dramaticidade e das jogadas fantásticas de animes como Super Campeões.
   - O jogo se passa na "Cidade do Futebol", uma metrópole vibrante onde o esporte é um estilo de vida e as lendas nascem no asfalto.
   - Seu objetivo é simples: começar como um atleta desconhecido e, através de desafios, torneios e partidas emocionantes, se tornar uma lenda dos campos de rua.
   - O nome "Urban" (Urbano) reflete toda a atmosfera do jogo: a cultura de rua, a energia da cidade, as quadras de asfalto e um visual noturno e energético, inspirado em néon e na vida da metrópole.

**2. A Tecnologia por Trás da Magia:**
   - **Narração com IA:** As partidas são narradas por uma Inteligência Artificial com a personalidade de narradores esportivos brasileiros, trazendo emoção a cada lance. É como ouvir um jogo no rádio, mas você está no controle!
   - **Voz da Várzea (TTS):** Usamos uma tecnologia de TTS (Text-to-Speech) para transformar o texto da narração em áudio, criando uma imersão completa.
   - **Sistema Robusto (Fallback):** Para garantir que o jogo nunca pare, usamos múltiplos provedores de IA (como Gemini, Groq e Cerebras). Se um deles "pedir pra sair", o outro entra em campo na hora, sem deixar a bola parar.

**3. Regras da Partida de Rua:**
   - **Objetivo Principal:** Vencer a partida! Simples assim.
   - **Vitória por Gols:** O primeiro time a marcar 3 gols vence.
   - **Derrota por Gols:** Se sofrer 3 gols, a partida acaba para você.
   - **Fim por Tempo:** Se ninguém marcar 3 gols após 10 rodadas (lances), o jogador com mais gols no placar vence. Empates são possíveis!

**4. Arquétipos de Personagens (Estilos de Jogo):**
   - **Velocista:** Focado em velocidade e ataque. Ideal para quem gosta de arrancar e deixar os adversários comendo poeira. Habilidade Especial: **Corrida Relâmpago**.
   - **Maestro:** O cérebro do time. Excelente em controle de bola e passes precisos. Habilidade Especial: **Passe Mágico**.
   - **O Artilheiro:** O matador. Sua especialidade é finalizar com chutes poderosos e precisos. Habilidade Especial: **Chute Poderoso**.
   - **Defensor:** Uma verdadeira muralha. Ótimo em bloqueios e desarmes. Habilidade Especial: **Bloqueio Imbatível**.
   - **Líder:** O coração da equipe. Inspira os companheiros com sua garra, sendo bom na defesa e na liderança. Habilidade Especial: **Comando de Equipe**.

**5. Contextos de Jogo (Situações da Partida):**
   - Suas opções de jogada (os cards) mudam dependendo do que está acontecendo em campo. Isso deixa o jogo mais tático.
   - **Meio-Campo:** Situação neutra, o momento de pensar e construir a jogada com dribles e passes.
   - **Ataque:** Você está perto do gol adversário, a pressão aumenta! É hora de buscar o chute ou um drible curto para se livrar do zagueiro.
   - **Chance Clara de Gol:** É agora ou nunca! Você está cara a cara com o goleiro. A única opção é encher o pé e chutar para o gol!
   - **Defesa Pressionada:** O time adversário está vindo com tudo. O foco é total em desarmes e ações defensivas para não sofrer o gol.

**6. Criação e Gerenciamento de Personagens:**
   - **Posso dar nome ao meu personagem?** Claro que sim! Depois de escolher um dos Arquétipos na tela de "Seleção de Jogadores", você poderá dar um nome único para a sua lenda do asfalto.
   - **Quantos personagens posso ter?** Você pode criar vários personagens! Cada um com um nome e um arquétipo diferente. Eles ficam todos salvos na sua conta.
   - **Onde vejo meus personagens?** Na tela "Meus Personagens", você pode ver todos os jogadores que criou, editar o nome deles ou escolher um para iniciar uma nova campanha.

**7. Campanhas Geradas por IA:**
   - **Como as campanhas são criadas?** Depois de criar seu personagem, a Inteligência Artificial irá gerar opções de campanhas exclusivas para ele, com nomes e descrições diferentes.
   - **Eu posso escolher a campanha?** Com certeza! A IA te dá as opções, mas a escolha final é sua. Você seleciona a campanha que mais te agrada na tela de "Seleção de Campanha" e aí sim a sua jornada começa.

**8. Aulinha do Mestre (Regras do Futebol):**
   - **O que é Impedimento?** Na várzea, a gente costuma dizer que "não tem impedimento" pra deixar o jogo mais dinâmico! Mas, se você quer saber a regra oficial: um jogador está em posição de impedimento se estiver mais perto da linha de gol adversária do que a bola e o penúltimo adversário no momento em que a bola é tocada para ele. Basicamente, é uma regra para evitar que os atacantes fiquem "plantados" na frente do gol esperando a bola. No Urban Soccer, essa regra é simplificada para a ação fluir melhor.
   - **O que é uma Falta?** É quando um jogador comete uma infração contra o adversário, como um carrinho perigoso, um empurrão ou tocar a bola com a mão (a não ser que seja o goleiro na sua área, claro). No nosso jogo, as faltas são narradas pela IA e podem resultar em lances de bola parada para o adversário.

--- FIM DO CONTEXTO ---

Com base estritamente no contexto acima, responda à seguinte pergunta do jogador de forma clara, direta e no espírito do "Mestre da Várzea":
Pergunta: "{user_question}"
"""

async def ask_faq_stream_and_collect(question: str, log_id: str = None) -> AsyncGenerator[str, None]:

    """
    Monta o prompt do FAQ no formato de mensagens e chama o provedor de LLM
    para obter uma resposta em streaming real, coletando a resposta completa.
    Se log_id for fornecido, atualiza o log com a resposta completa ao final.
    """

    from ..models import faq_log_model
    
    full_prompt = FAQ_CONTEXT_PROMPT_TEMPLATE.format(user_question=question)

    messages = [
        {"role": "user", "content": full_prompt}
    ]
    
    collected_response = ""
    
    try:
        logger.info(f"Iniciando stream de FAQ para a pergunta: '{question}'")
        async for token in llm_provider.stream_with_fallback(messages):
            collected_response += token
            yield token
            
        if log_id and collected_response:
            success = await faq_log_model.update_faq_log_answer(log_id, collected_response)
            if success:
                logger.info(f"Resposta salva no log {log_id}")
            else:
                logger.error(f"Falha ao salvar resposta no log {log_id}")
            
    except Exception as e:
        logger.error(f"Erro crítico durante o stream do FAQ: {e}")
        error_message = "Opa, parece que o microfone aqui falhou! O Mestre da Várzea está resolvendo um problema técnico. Tente de novo daqui a pouco."
        
        if log_id:
            await faq_log_model.update_faq_log_answer(log_id, error_message)
            
        yield error_message


async def generate_conversation_title(question: str) -> str:
    
    """
    Gera um título curto e descritivo para a conversa baseado na primeira pergunta.
    """
    
    title_prompt = f"""
Crie um título curto e descritivo (máximo 6 palavras) para uma conversa que começou com esta pergunta sobre o jogo Urban Soccer:

Pergunta: "{question}"

Responda APENAS com o título, sem aspas ou explicações. O título deve capturar o tema principal da pergunta de forma concisa.

Exemplos de bons títulos:
- "Regras do Jogo"
- "Arquétipos de Personagens"  
- "Sistema de Campanhas"
- "Dicas para Iniciantes"
"""

    messages = [{"role": "user", "content": title_prompt}]
    
    try:
        title = ""
        async for token in llm_provider.stream_with_fallback(messages):
            title += token
            
        title = title.strip().replace('"', '').replace("'", "")
        
        if len(title) > 50 or len(title) < 3:
            return "Nova Conversa FAQ"
            
        return title
        
    except Exception as e:
        logger.error(f"Erro ao gerar título da conversa: {e}")
        return "Nova Conversa FAQ"

async def ask_faq_stream(question: str) -> AsyncGenerator[str, None]:

    """
    Monta o prompt do FAQ no formato de mensagens e chama o provedor de LLM
    para obter uma resposta em streaming real.
    """

    full_prompt = FAQ_CONTEXT_PROMPT_TEMPLATE.format(user_question=question)

    messages = [
        {"role": "user", "content": full_prompt}
    ]
    
    try:
        logger.info(f"Iniciando stream de FAQ para a pergunta: '{question}'")
        async for token in llm_provider.stream_with_fallback(messages):
            yield token
            
    except Exception as e:
        logger.error(f"Erro crítico durante o stream do FAQ: {e}")
        yield "Opa, parece que o microfone aqui falhou! O Mestre da Várzea está resolvendo um problema técnico. Tente de novo daqui a pouco."