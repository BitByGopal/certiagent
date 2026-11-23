"""LangGraph orchestrator: intake -> extraction -> (registry || forensics) -> reasoning."""
from typing import Any, Optional, TypedDict
from PIL import Image
from langgraph.graph import StateGraph, START, END
from agents import intake, extraction, registry, forensics, reasoning


class State(TypedDict, total=False):
    image: Any
    mode: str                 # "llm" or "rules"
    ocr_text: str
    ocr_confidence: float
    fields: dict
    extraction_mode: str
    registry: dict
    forensics: dict
    ela_map: Any
    verdict: str
    evidence: list
    explanation: str


def intake_node(s: State):     return intake.run(s["image"])
def extract_node(s: State):    return extraction.run(s["ocr_text"], s.get("mode", "llm"))
def registry_node(s: State):   return registry.run(s["fields"])
def forensics_node(s: State):  return forensics.run(s["image"])
def reasoning_node(s: State):
    return reasoning.run(s["registry"], s["forensics"], s["ocr_confidence"], use_llm=s.get("mode", "llm") == "llm")


def build():
    g = StateGraph(State)
    g.add_node("intake", intake_node) 
    g.add_node("extraction", extract_node)
    g.add_node("registry_check", registry_node)
    g.add_node("forensics_check", forensics_node)
    g.add_node("reasoning", reasoning_node)
    g.add_edge(START, "intake")
    g.add_edge("intake", "extraction")
    g.add_edge("extraction", "registry_check")     # these two run in parallel
    g.add_edge("extraction", "forensics_check")
    g.add_edge(["registry_check", "forensics_check"], "reasoning")  # wait for both
    g.add_edge("reasoning", END)
    return g.compile()


APP = build()


def verify(image: Image.Image, mode: str = "llm") -> State:
    return APP.invoke({"image": image.convert("RGB"), "mode": mode})


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/certificates/000_genuine.png"
    out = verify(Image.open(path))
    print("Mode      :", out["extraction_mode"])
    print("Fields    :", out["fields"])
    print("Registry  :", out["registry"]["status"], out["registry"]["mismatches"])
    print("ELA score :", out["forensics"]["ela_score"])
    print("VERDICT   :", out["verdict"])
    print("Why       :", out["explanation"])
