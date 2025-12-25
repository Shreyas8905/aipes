import os
import fitz  
import base64
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from loader import BatchLoader
import shutil

class AgentState(BaseModel):
    file_path: str
    team_name: str
    raw_text: str = ""
    image_paths: List[str] = []

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_node(state: AgentState):
    doc = fitz.open(state.file_path)
    text_content = ""
    img_paths = []
    
    output_dir = f"temp_images/{state.team_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, page in enumerate(doc):
        if i > 5: break
        text_content += page.get_text() + "\n"
        images = page.get_images(full=True)
        for j, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            img_path = f"{output_dir}/page_{i}_img_{j}.{ext}"

            with open(img_path, "wb") as f:
                f.write(image_bytes)

            img_paths.append(img_path)

    print({"raw_text": text_content, "image_paths": img_paths})
        
    return {
    "file_path": state.file_path,
    "team_name": state.team_name,
    "raw_text": text_content,
    "image_paths": img_paths
    }


loader = BatchLoader(source_config="test_ppts")

files = loader.fetch_files()

if not files:
        print({"message": "No PDFs found in 'test_ppts' folder."})
else:      
    print(f"[AIPES] Queuing {len(files)} files for evaluation...")
    file_data = files[0]



workflow = StateGraph(AgentState)

workflow.add_node("extractor", extract_node)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", END)

app_graph = workflow.compile()

initial_state = AgentState(
    file_path=file_data["path"],
    team_name=file_data["team_name"]
)

temp_dir = os.path.join("temp_images", file_data["team_name"])

try:
    result = app_graph.invoke(initial_state)
    print("FINAL RESULT:", result)
finally:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


