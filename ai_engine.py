import os
import fitz  
import base64
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

class DesignReport(BaseModel):
    quality_summary: str = Field(description="Review of aesthetics, font clarity, and professionalism")
    missing_fields: List[str] = Field(description="List of missing standard elements like Title, Team Name, etc.")

class ContentReport(BaseModel):
    problem_solution_fit: str
    feasibility_analysis: str
    uniqueness_analysis: str
    content_quality_summary: str

class FinalScoreCard(BaseModel):
    team_name: str
    ppt_quality_score: int
    content_quality_score: int
    problem_solution_fit_score: int
    feasibility_score: int
    uniqueness_score: int
    reasoning: str

class AgentState(BaseModel):
    file_path: str
    team_name: str
    raw_text: str = ""
    image_paths: List[str] = []
    design_report: Optional[DesignReport] = None
    content_report: Optional[ContentReport] = None
    final_score: Optional[FinalScoreCard] = None

llm_text = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
llm_vision = ChatGroq(model="llama-3.2-11b-vision-preview", temperature=0)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_node(state: AgentState):
    """Agent 1: Extracts Text & Images from PDF"""
    doc = fitz.open(state.file_path)
    text_content = ""
    img_paths = []
    
    output_dir = f"temp_images/{state.team_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, page in enumerate(doc):
        if i > 5: break 
        text_content += page.get_text() + "\n"
        pix = page.get_pixmap(dpi=100)
        img_path = f"{output_dir}/slide_{i}.png"
        pix.save(img_path)
        img_paths.append(img_path)
        
    return {"raw_text": text_content, "image_paths": img_paths}

def design_eval_node(state: AgentState):
    """Agent 2: Checks Visual Quality (Vision Model)"""
    selected_images = state.image_paths[:3]
    
    messages = [
        {"type": "text", "text": "Analyze these slides for visual clarity, professionalism, and missing fields (Title, Team Name). Output JSON."}
    ]
    
    for img_path in selected_images:
        b64 = encode_image(img_path)
        messages.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })
    
    structured_llm = llm_vision.with_structured_output(DesignReport)
    response = structured_llm.invoke([HumanMessage(content=messages)])
    return {"design_report": response}

def content_eval_node(state: AgentState):
    """Agent 3: Checks Logical Content (Text Model)"""
    prompt = ChatPromptTemplate.from_template(
        """
        Analyze this pitch deck text:
        {text}
        
        Evaluate: Problem-Solution Fit, Feasibility, Uniqueness.
        """
    )
    chain = prompt | llm_text.with_structured_output(ContentReport)
    response = chain.invoke({"text": state.raw_text})
    return {"content_report": response}

def scoring_node(state: AgentState):
    """Agent 4: Final Scorer"""
    prompt = ChatPromptTemplate.from_template(
        """
        Act as a Venture Capitalist Judge. Assign scores (0-20) based on these reports.
        
        Team: {team_name}
        Design Report: {design_report}
        Content Report: {content_report}
        """
    )
    chain = prompt | llm_text.with_structured_output(FinalScoreCard)
    
    response = chain.invoke({
        "team_name": state.team_name,
        "design_report": state.design_report.model_dump_json(),
        "content_report": state.content_report.model_dump_json()
    })
    return {"final_score": response}

workflow = StateGraph(AgentState)
workflow.add_node("extractor", extract_node)
workflow.add_node("design_agent", design_eval_node)
workflow.add_node("content_agent", content_eval_node)
workflow.add_node("scorer", scoring_node)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "design_agent")
workflow.add_edge("extractor", "content_agent")
workflow.add_edge("design_agent", "scorer")
workflow.add_edge("content_agent", "scorer")
workflow.add_edge("scorer", END)

app_graph = workflow.compile()

async def run_ai_pipeline(file_data: dict):
    initial_state = AgentState(
        file_path=file_data["path"],
        team_name=file_data["team_name"]
    )
    result = await app_graph.ainvoke(initial_state)
    return result["final_score"].dict()