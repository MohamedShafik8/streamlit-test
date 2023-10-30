import streamlit as st
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import StreamlitCallbackHandler
# Set OpenAI API key
openai.api_key  = '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'
openai_history = []
# Function to get completion
def get_completion(relation, emotion, resolution, context):
    openai_api_key = "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"
    chat = ChatOpenAI(temperature=0.7, model='gpt-3.5-turbo', openai_api_key=openai_api_key, streaming=True, callbacks=[StreamlitCallbackHandler(st.container())])

    template_string = '''
    Your task is to serve as an immediate aid guiding users through a structure and actionable step-by-step guide to resolve a disagreement between two {relation} by providing creative resolutions that do not include seeking professional help. 

    Consider the following details:

    relationship : {relation}
    Emotional Impact: {emotion}
    Objective: {resolution}
    Scenario: {context}

    Please provide a step-by-step guide in detailed bullet points, providing clear, creative, and actionable pathways on how to achieve the desired {resolution} in context to the users {relation}, given the {emotion} and {context}. Your steps should address all the issues mentioned in the {context}. Don't make general statements that apply in any situation.
    '''

    prompt_template = ChatPromptTemplate.from_template(template_string)
    message = prompt_template.format_messages(relation=relation, emotion=emotion, resolution=resolution, context=context)

    response = chat(message)
    st.session_state['chat_active'] = True
    return response.content


global chat_start
chat_start = 'Hello, I am the AiOS Inter Accomplish Assistant. I am here to help you with conflict resolution and related subjects. Can I assist you further with any question you may have about my initial recommendation?'

def run_chat(ans):
    global chat_start
    openai_history.clear()
    context = f'''You are the AiOS Inter Accomplish Assistant, designed to to provide helpful answers to user's questions. The user has a conflict they are trying to resolve, below is the background:
    Your recommendation: {ans}
    Please help the user with any questions they may have about your initial recommendation. 
    '''
    openai_history.append({'role':'system', 'content':context})
    openai_history.append({'role':'user', 'content':'Hi!'})
    openai_history.append({'role':'assistant', 'content':chat_start})
    return

def get_chat_completion(message, chat_history):
    openai_history.append({'role':'user', 'content':message})

    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=openai_history,
    ).choices[0].message["content"]

    openai_history.append({'role':'assistant', 'content':response})
    chat_history.append((message, response))

    return '', chat_history



if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if 'chat_active' not in st.session_state:
    st.session_state['chat_active'] = False

# UI elements
st.title('AiOS Inter Accomplish Assistant')

relation = st.selectbox('Relationship Category', ['Co-workers', 'Family Members', 'Friends', 'Romantic Partners'])
emotion = st.selectbox('Emotional Impact', ['Calm', 'Concerned', 'Annoyed', 'Upset', 'Overwhelmed'])
resolution = st.selectbox('Resolution Type', ['Compromise', 'Confrontation', 'Understanding', 'Avoidance', 'Accommodation'])
context = st.text_area('Other Info')

submit_button = st.button('Submit')

if submit_button:
    response = get_completion(relation, emotion, resolution, context)
    #st.text_area("Response", response, height=300)

st_callback = StreamlitCallbackHandler(st.container())


