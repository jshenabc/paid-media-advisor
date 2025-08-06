from langchain_ibm import WatsonxLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# WatsonX.ai 
watsonx_llm = WatsonxLLM(
    model_id="meta-llama/llama-3-2-90b-vision-instruct", 
    url="https://us-south.ml.cloud.ibm.com", 
    apikey=os.getenv("WATSONX_API_KEY"),  
    project_id=os.getenv("WATSONX_PROJECT_ID"), 
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 500,
        "temperature": 0.3,
        "repetition_penalty": 1.0,
    }
)

prompt = PromptTemplate.from_template("""
You are a marketing advisor AI. Based on the user question and model output, write a one-paragraph campaign strategy recommendation. if query is asking a prediction of roi, check the projected_roi.

Question: {query}
Model Output: {performance_analysis}

Recommendation:
""")

chain = LLMChain(llm=watsonx_llm, prompt=prompt)

def generate_strategy(query: str, performance_analysis: str) -> str:
    try:
        result = chain.run({"query": query, "performance_analysis": performance_analysis})
        return result
    except Exception as e:
        return f"Strategy generation error: {str(e)}"