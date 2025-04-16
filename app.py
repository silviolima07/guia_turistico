import streamlit as st
import openai
import base64
from PIL import Image
from io import BytesIO
import os
from groq import Groq
from dotenv import load_dotenv



def generate_city_description_groq(city, topico):
    """Gera uma descrição textual detalhada sobre a cidade usando Groq/Llama 3"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um guia turístico especializado em cidades brasileiras. Descreva em detalhes os principais pontos turísticos, cultura, gastronomia e características únicas da cidade. Use um tom entusiasmado e informativo. Responda em português."
                },
                {
                    "role": "user",
                    "content": f"Descreva a cidade de {city}.Responda apenas e somente sobre {topico}. Texto curto, apenas 100 caracteres. Formate e use {topico} como titulo de uma seção.."
                }
            ],
            model="llama3-70b-8192",  # Modelo mais potente da Groq
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar descrição com Groq: {str(e)}")
        return None

def artist(city):
    # Gera a imagem com DALL-E 3
    image_response = openai.images.generate(
        model="dall-e-3",
        prompt=f"""Uma imagem representando férias em {city}, mostrando pontos turísticos icônicos e cultura local em estilo pop-art vibrante.
        Estilo: Ilustração digital colorida com tons vibrantes.""",
        size="1024x1024",
        n=1,
        response_format="b64_json",
    )
    
    # Processa a imagem
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_data))
    image.save(f"{city}_vacation.png")
    
    # Gera a descrição textual com Groq
    description = generate_city_description_groq(city, topico)
    
    return image, description

# Interface Streamlit
st.set_page_config(page_title="Guia Turístico IA", page_icon="🌎")
st.title("🌴 Guia Turístico de Cidades Brasileiras")

travel = Image.open('img/travel.png')

logo = Image.open("img/logo.png")
st.sidebar.image(logo, caption="", use_container_width=True)

load_dotenv()

# Configuração de API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = Groq(api_key=GROQ_API_KEY)

# Sidebar com configurações
with st.sidebar:
    st.header("Configurações")
    city = st.text_input("Digite uma cidade brasileira:", "Rio de Janeiro")
    #estilo = st.selectbox("Estilo da imagem:", ["Pop Art", "Realista", "Aquarela", "Pixel Art"])
    topico = st.selectbox("Tópicos:", ["Cultura Local", "Melhores Meses", "Gasto Médio Diário", "Gastronomia"])

if st.button("Criar Guia Completo", type="primary"):
    with st.spinner(f"Gerando guia turístico para {city}..."):
        col1, col2 = st.columns(2)
        col11, col22 = st.columns(2)
        
        
        try:
            #image, description = artist(city)
            # Gera a descrição textual com Groq
            description = generate_city_description_groq(city, topico)
            
            with col1:
                st.image(travel, caption="", use_container_width=True)
            
            with col2:
                st.subheader(f"📌 {city} - Guia Completo")
                st.markdown(description)
                
                # Seção adicional gerada pelo Groq
            with col11:
                with st.expander("🗓️ Melhor época para visitar"):
                    periodo = client.chat.completions.create(
                        messages=[
                            {"role": "user", "content": f"Qual a melhor época para visitar {city}? Responda em 3 linhas no máximo."}
                        ],
                        model="llama3-70b-8192",
                        max_tokens=150
                    )
                    st.write(periodo.choices[0].message.content)
            
                
                with st.expander("🍽️ Pratos típicos para experimentar"):
                    comidas = client.chat.completions.create(
                        messages=[
                            {"role": "user", "content": f"Liste 3 pratos típicos de {city} com descrição breve de cada um. Formate como lista markdown."}
                        ],
                        model="llama3-70b-8192",
                        max_tokens=200
                    )
                    st.markdown(comidas.choices[0].message.content)
                
        except Exception as e:
            st.error(f"Erro ao gerar conteúdo: {str(e)}")
            st.info("Verifique suas chaves de API e conexão com a internet")

# Rodapé
st.divider()
st.caption("Desenvolvido com Groq (Llama 3) e OpenAI (DALL-E 3) | © 2024")