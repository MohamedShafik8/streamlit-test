import streamlit as st
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import GmailToolkit
from langchain.tools.gmail.utils import build_resource_service, get_gmail_credentials
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from bs4 import BeautifulSoup
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage
import re


class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


def gmail(input):
    credentials = get_gmail_credentials(token_file="token.json",scopes=["https://mail.google.com/"],client_secrets_file="credentials.json",)
    api_resource = build_resource_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    #toolkit = GmailToolkit()
    tools = toolkit.get_tools()
    #print(tools)
    llm = OpenAI(temperature=0.1,openai_api_key="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")
    agent = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, output_parser=CustomOutputParser())
    return agent.run(input)

with st.sidebar:
    st.markdown("## Uncover Personalized Paths for Child Wellbeing")
    st.markdown("""
Navigate parenting challenges with ease:
- **Assess Situations**: Quickly analyze behaviors, emotions, and environmental contexts.
- **Tailored Recommendations**: Get actionable advice suited to your child's age.
- **Practical Strategies**: Apply effective, concise steps designed for your child's unique development stage.

Empower your parenting journey with customized guidance for enhancing your child's growth and happiness.
""")
    st.markdown("---") 
    st.markdown("### Instructions")
    st.markdown("""
Navigate parenting challenges with ease:
- **Situation**: Choose one that fits.
- **Emotion**: What emotion is being shown?
- **Environment**: Where You Notice the Behavior Most. 
- **Age**: Age Range. 

Empower your parenting journey with customized guidance for enhancing your child's growth and happiness.
""")
    st.markdown("---") 
    st.markdown("## Follow and Support Us")
    st.markdown("""
    <h3>Follow us for the latest updates and expert insights on childcare:</h3>
    
    <a href="https://www.facebook.com/YourPage" target="_blank" style="margin-right: 20px; text-decoration: none;">
        <img src="https://seeklogo.com/images/F/facebook-icon-logo-819DD0A07B-seeklogo.com.png" alt="Facebook" style="width: 24px; height: 24px;"/>
    </a>
    <a href="https://twitter.com/YourPage" target="_blank" style="margin-right: 20px; text-decoration: none;">
        <img src="https://img.freepik.com/free-vector/new-twitter-logo-x-icon-black-background_1017-45427.jpg?size=338&ext=jpg&ga=GA1.1.1880011253.1698969600&semt=ais" alt="Twitter" style="width: 24px; height: 24px;"/>
    </a>
    <a href="https://www.instagram.com/YourPage" target="_blank" style="margin-right: 20px; text-decoration: none;">
        <img src="https://img.freepik.com/premium-vector/purple-gradiend-social-media-logo_197792-1883.jpg?size=338&ext=jpg&ga=GA1.1.1880011253.1699056000&semt=ais" alt="Instagram" style="width: 24px; height: 24px;"/>
    </a>
    <a href="https://www.linkedin.com/company/YourPage" target="_blank" style="margin-right: 20px; text-decoration: none;">
        <img src="https://png.pngtree.com/element_our/png/20181011/linkedin-social-media-icon-design-template-vector-png_127000.jpg" style="width: 24px; height: 24px;"/>
    </a>
    
    <p>We value your support!</p>
    """, unsafe_allow_html=True)
    email_sidebar = st.text_input("Enter your email to join")
    submit = st.button('Submit', key='button')
    if submit:
        email="""send an email ,subject: Welcome to Life Solutions!, input message:Welcome to Life solutions! // recipents:"""
        email_final= email + email_sidebar
        gmail(email_final)
    

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


# UI elements
st.title('AiOS Inter Accomplish Assistant')

relation = st.selectbox('Relationship Category', ['Co-workers', 'Family Members', 'Friends', 'Romantic Partners'])
emotion = st.selectbox('Emotional Impact', ['Calm', 'Concerned', 'Annoyed', 'Upset', 'Overwhelmed'])
resolution = st.selectbox('Resolution Type', ['Compromise', 'Confrontation', 'Understanding', 'Avoidance', 'Accommodation'])
context = st.text_area('Other Info')

submit_button = st.button('Submit', key='submit_button')

if submit_button:
    response = get_completion(relation, emotion, resolution, context)
    #st.text_area("Response", response, height=300)
    st_callback = StreamlitCallbackHandler(st.container())
    with st.container():
        st.markdown("### Your output in your inbox!")
        feedback = st.text_area("Would you like the output to be send to you, provide the email here.")
        email2="""send an email ,subject: Welcome to Life Solutions!, input message:Welcome to Life solutions!"""
        text=response
        final_output= email2+text+feedback
        gmail(final_output)
        #gmail_send = st.button('Submit', key='gmail_send_button')
    #if gmail_send:
        #print(feedback)
        #print(response)
            #first="""send an email,subject: Welcome to Life Solutions!, input message:Welcome to Life solutions!"""
            #input= first + response.content +"// recipents:"+ feedback
        #email2="""send an email ,subject: Welcome to Life Solutions!, input message:Welcome to Life solutions!"""
        #text=response.content
        #final_output= email2+text+feedback
        #gmail(final_output)



