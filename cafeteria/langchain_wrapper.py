
# from langchain.schema.output_parser import StrOutputParser
# from langchain.schema.runnable import RunnableLambda
# from langchain.schema.runnable.passthrough import RunnableAssign
# from langchain.document_transformers import LongContextReorder
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyMuPDFLoader,ArxivLoader
# from langchain.chains import RetrievalQA
# from langchain.schema import Document
# from langchain_ollama import OllamaLLM
# from faiss import IndexFlatL2
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_core.documents import Document

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import TavilySearchResults
from langgraph.graph import START, StateGraph
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate,SystemMessagePromptTemplate
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.tools import tool
from langchain_aws import ChatBedrockConverse

import langchain
langchain.debug = True

from .models import Menu

from typing_extensions import List, TypedDict
import json
import os
import pandas as pd
from functools import partial
from operator import itemgetter
import boto3
from botocore.config import Config
import json

if os.getenv("GOOGLE_API_KEY") == None:
    GOOGLE_API_KEY = '<insert password!>'
else:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if os.getenv("TAVILY_API_KEY") == None:
    TAVILY_API_KEY = '<insert password!>'
else:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if os.getenv("AWS_ACCESS_KEY") == None:
    AWS_ACCESS_KEY = '<insert password!>'
else:
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")

if os.getenv("AWS_SECRET_KEY") == None:
    AWS_SECRET_KEY = '<insert password!>'
else:
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")


os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY


class LLM_Service:
    def __init__(self):
        # self.llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash",
        #     temperature=1.0,
        #     max_tokens=None,
        #     timeout=None,
        #     max_retries=2,
        # )
        # Initialize Bedrock client
        self.llm = ChatBedrockConverse(
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Specify the model ID
            temperature=1.0,
            max_tokens=None
        )

        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.tavily_search_tool = TavilySearchResults()

        ## load paper
        index_path = "./cafeteria/static/docstore_index"
        paper_docs = FAISS.load_local(index_path,allow_dangerous_deserialization=True, embeddings=self.embeddings)
        self.paper_docs = paper_docs.as_retriever()

        ## test
        # df = pd.read_csv("./cafeteria/static/assets/menulist.csv")
        menus = list(Menu.objects.all().values())
        df = pd.DataFrame(menus)
        df = df[df['showmeal'] == 1]
        meal_recommender = create_pandas_dataframe_agent(self.llm, 
                                                        df, 
                                                        verbose=False,
                                                        allow_dangerous_code=True,
                                                        agent_executor_kwargs={"handle_parsing_errors": True})
        
        nutrient_list = ['energy','protein','fat','carbohydrate','fiber','calcium','veggies']
        nutrient_unit = ['kcal','gr','gr','gr','gr','mg','gr']

        class State(TypedDict):
            additional_notes :str
            notes_history:List[str]
            detail_nutritions: List[str]
            min_nutritions: List[int]
            recommended_meal_detail: str
            list_meals: List[str]
            verbose_in_function: bool = False

        def initial_state(state: State):
            return {
                "detail_nutritions":[],
                "min_nutritions":[]
                }
        # @tool
        def retrieve_papers(query: str) -> str:
            """Retrieve relevant papers from the FAISS vector store based on the query."""
            print(f"Input retieve papers: {query}")
            # Use the FAISS retriever to search for documents
            retrieved_docs = paper_docs.similarity_search(query, k=3)  # Adjust 'k' for the number of papers to retrieve
            # Return a string of the top retrieved documents
            print(f"Retrieved docs: {retrieved_docs}")
            return "\n".join([doc.page_content for doc in retrieved_docs])
        
        nutritionist_agent = self.llm
        # nutritionist_agent = self.llm.bind_tools([self.tavily_search_tool])
        prompt_nutritionist = ChatPromptTemplate([
            SystemMessagePromptTemplate.from_template(
                "You are a highly experienced nutritionist. Your task is to recommend the minimum intake of specific nutrients tailored to the user's profile. Ensure your responses are scientifically backed, clear, and concise. Provide credible references when possible, and avoid unnecessary details."
            ),
            HumanMessagePromptTemplate.from_template(
                "You are recommending the minimum intake of the following nutrients in their respective units:\n"
                "{nutrient} in {unit}\n\n"
                "**Guidelines:**\n"
                "- Consider notes provided by the user: {additional_notes}.\n"
                "- Include relevant historical information if available: {notes_history}.\n"
                "- Provide one concise scientific rationale for each nutrient.\n"
                "- Return the result strictly in JSON format. Ensure the order of the nutrients matches the input list: {nutrient}.\n"
                "- Format the JSON output as follows:\n"
                "  - `reason` (list of strings): Scientific rationale for each nutrient, with APA citation.\n"
                "  - `minimum` (list of integers): Minimum intake recommendation for each nutrient.\n"
                "\n"
                "**Output Format Example:**\n"
                '{{\n'
                '  "reason": ["More calories are needed due to energy expenditure", "Protein is required for muscle repair"],\n'
                '  "minimum": [2000, 60]\n'
                '}}\n\n'
                "**Ensure the output strictly follows this format and matches the order of the input list. Do not include any extra text.**"
            )
        ])

        def generate_nutrition_from_paper(state: State):
            state['nutrient'] = nutrient_list
            state['unit'] = nutrient_unit
            messages = prompt_nutritionist.invoke(state) # this is just formatting
            if state['verbose_in_function']: print('generate_nutrition_from_paper messages : ',messages)
            response = nutritionist_agent.invoke(messages)
            if state['verbose_in_function']: print('generate_nutrition_from_paper response : ',response)
            cleaned_response = response.content.strip("`").strip('json').strip('\n\n') # changed
            if state['verbose_in_function']: print('generate_nutrition_from_paper cleaned : ',cleaned_response)
            cleaned_response = json.loads(cleaned_response)

            state['detail_nutritions'] = cleaned_response['reason']
            state['min_nutritions'] = cleaned_response['minimum']

            return state



        """
            The meal reecommender agent will
            1. Get access to dataframe of menu,
            2. Able to execute pandas script, this one is handled in the back-end by LangGraph
            3. Uses min_nutritions to generate meal,
            4. GENERATING MEAL OFTEN FAIL, that's why there is while-loop inside.
        """
        prompt_meal_recommender = ChatPromptTemplate([
            SystemMessagePromptTemplate.from_template(
                "You are an expert meal planner creating personalized meal recommendations based on user preferences and nutritional needs. "
                "Your responses should be engaging, appealing, and adhere strictly to the provided menu."
            ),
            HumanMessagePromptTemplate.from_template(
                "Generate a meal plan that aligns with the following criteria:\n"
                "- **User Notes:** {additional_notes}\n"
                "- **Nutritional Guidelines:** {stringify_nutrient_recommendation}\n"
                "- **Meal History (if available):** {notes_history}\n\n"
                "**Guidelines:**\n"
                "1. Ensure all meals follow the given nutritional targets.\n"
                "2. Combine meals creatively while staying within the available menu.\n"
                "3. Maintain an engaging and positive tone to appeal to the user.\n"
                "4. Do **not** include meals that are not explicitly listed in the menu.\n"
                "5. Use exact names from the menu under `meal_name`.\n"
                "6. Avoid special characters and markdown (e.g., *, _, or [ ]).\n"
                "7. Consider personal preferences mentioned in {additional_notes}.\n"
                "\n"
                "Now, generate a meal plan that meets these criteria."
            )
        ])

        def generate_meal_set(state:State):
            # reformat the min range
            # assume three times meal for one day
            list_of_meal = []
            attempt = 0
            while len(list_of_meal) == 0:
                attempt +=1 
                if state['verbose_in_function']: print('Cooking attempt : ',attempt)
                stringify_recommendation = ""
                for a in range(len(nutrient_list)):
                    stringify_recommendation += f"{nutrient_list[a]}: {(state['min_nutritions'][a] / 3):.1f} {nutrient_unit[a]}, "


                state["stringify_nutrient_recommendation"] = stringify_recommendation

                response = meal_recommender.invoke(prompt_meal_recommender.invoke(state))
                if state['verbose_in_function']: print('generate_meal_set response : ',stringify_recommendation)
                list_of_meal = [meal for meal in df['meal_name'].str.lower() if meal in response['output'].lower()]

                ## remove (small) (middle) (large) from the recommended meal detail
                recommended_meal_detail = response['output']
                recommended_meal_detail = recommended_meal_detail.replace('*','')
            return {
                'recommended_meal_detail':recommended_meal_detail,
                'list_meals':list_of_meal
            }
            
        """
            Build the graph.
        """
        graph_builder = StateGraph(State).add_sequence([
            initial_state,
            generate_nutrition_from_paper,
            generate_meal_set])# 
        graph_builder.add_edge(START, "initial_state")
        self.graph = graph_builder.compile()
    
    def predict(self,query,notes_history=[]):
        return self.graph.invoke({
            'additional_notes':query,
            'notes_history':notes_history,
            'verbose_in_function':True
        })