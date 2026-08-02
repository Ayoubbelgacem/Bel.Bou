# api/server.py
import multiprocessing
import io
import contextlib
import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Racine du projet (pour que les imports src.* fonctionnent)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

app = FastAPI(title="Bou.Bel API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TIMEOUT_SECONDS = 5
MAX_CODE_LENGTH = 50_000

class CodeRequest(BaseModel):
    code: str = Field(..., description="Code source Bou.Bel (.bou)")
    mode: str = Field("vm", description="'vm' ou 'interpreter'")
    debug: bool = False

class RunResult(BaseModel):
    success: bool
    output: str
    error: str | None = None

def _run_in_subprocess(code: str, mode: str, debug: bool, result_queue):
    output_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(output_buffer):
            from src.lexer.tokenizer import Tokenizer
            from src.parser.parser import Parser

            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()
            parser_obj = Parser(tokens)
            ast = parser_obj.parse()

            stdlib_dir = os.path.join(PROJECT_ROOT, 'stdlib')
            search_paths = [PROJECT_ROOT, stdlib_dir, os.getcwd()]

            if mode == "vm":
                from src.vm.compiler import Compiler
                from src.vm.vm import VM
                compiler = Compiler(search_paths=search_paths)
                bytecode = compiler.compile(ast)
                vm = VM(search_paths=search_paths)
                vm.run(bytecode, debug=debug)
            else:
                from src.interpreter.interpreter import Interpreter
                interpreter = Interpreter(debug=debug)
                interpreter.module_search_paths = search_paths
                interpreter.interpret(ast)

        result_queue.put({
            "success": True,
            "output": output_buffer.getvalue(),
            "error": None,
        })
    except Exception as e:
        result_queue.put({
            "success": False,
            "output": output_buffer.getvalue(),
            "error": str(e),
        })

def execute_code(code: str, mode: str, debug: bool) -> dict:
    ctx = multiprocessing.get_context("spawn")
    result_queue = ctx.Queue()
    process = ctx.Process(
        target=_run_in_subprocess,
        args=(code, mode, debug, result_queue),
    )
    process.start()
    process.join(timeout=TIMEOUT_SECONDS)

    if process.is_alive():
        process.terminate()
        process.join()
        return {
            "success": False,
            "output": "",
            "error": f"Temps d'exécution dépassé ({TIMEOUT_SECONDS}s).",
        }

    if not result_queue.empty():
        return result_queue.get()

    return {
        "success": False,
        "output": "",
        "error": "Le programme s'est arrêté de façon inattendue.",
    }

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Bou.Bel API"}

@app.post("/run", response_model=RunResult)
def run_code(req: CodeRequest):
    if len(req.code) > MAX_CODE_LENGTH:
        return RunResult(
            success=False,
            output="",
            error=f"Code trop long (max {MAX_CODE_LENGTH} caractères).",
        )
    if req.mode not in ("vm", "interpreter"):
        return RunResult(
            success=False,
            output="",
            error="Le paramètre 'mode' doit être 'vm' ou 'interpreter'.",
        )
    result = execute_code(req.code, req.mode, req.debug)
    return RunResult(**result)