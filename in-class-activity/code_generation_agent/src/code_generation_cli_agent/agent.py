from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import shutil

from .llm import OllamaLLM
from .prompt_manager import PromptManager
from .tools import Tools
from .types import AgentConfig, RunResult
from .utils import strip_code_fences
import re

class Agent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.repo = Path(cfg.repo).resolve()
        self.tools = Tools(self.repo)
        self.prompt_manager = PromptManager()
        
        # Default prompt variants
        self.planning_variant = 'default'
        self.code_gen_variant = 'default'

    def _log(self, message: Any) -> None:
        if self.cfg.verbose:
            print(message)

    def _llm(self) -> OllamaLLM:
        return OllamaLLM(
            model=self.cfg.model,
            host=self.cfg.host,
            temperature=self.cfg.temperature,
        )

    def _call_llm(self, prompt: str) -> str:
        return self._llm().generate(prompt)

    def _multi_step_chain(self) -> Callable[[str], str]:
        try:
            from langchain_core.runnables import RunnableLambda
        except Exception:
            return self._call_llm

        return RunnableLambda(self._call_llm).invoke

    def create_program(self, desc: str, module_path: str) -> RunResult:
        """Create a program module.
        
        Steps:
        1) produce a plan
        2) draft code
        3) write to disk
        """
        run = self._multi_step_chain()

        # Plan
        p1 = self.prompt_manager.get_prompt(
            'planning',
            self.planning_variant,
            desc=desc,
            module_path=module_path
        )
        self._log(p1)
        plan = run(p1).strip()
        if not plan:
            return RunResult(False, "Model returned empty plan.")

        # Draft code
        p2 = self.prompt_manager.get_prompt(
            'code_generation',
            self.code_gen_variant,
            desc=desc,
            module_path=module_path,
            plan=plan
        )
        self._log(p2)
        draft_raw = run(p2)
        self._log(draft_raw)
        draft = strip_code_fences(draft_raw)
        if not draft.strip():
            return RunResult(False, "Model returned empty module draft.")

        final_code = draft.rstrip() + "\n"

        # Detect multi-file scaffold using FILE: <path> ... END_FILE markers.
        # Accept either `FILE: path` or `[FILE: path]` (marker may be at line start).
        file_blocks = re.findall(
            r"^[ \t]*\[?FILE:\s*(.+?)\]?\r?\n(.*?)\r?\n^[ \t]*\[?END_FILE\]?\s*$",
            final_code,
            re.DOTALL | re.MULTILINE,
        )

        if file_blocks:
            self._log(f"Detected {len(file_blocks)} file blocks in LLM draft; scaffolding...")
            for f_path, f_content in file_blocks:
                f_path = f_path.strip()

                # Skip any test-related files or tests/ directories
                name = Path(f_path).name
                parts = [p.lower() for p in Path(f_path).parts]
                if 'tests' in parts or name.startswith('test_'):
                    self._log(f"Skipping test file: {f_path}")
                    continue

                # strip any surrounding code fences inside each block
                content = strip_code_fences(f_content).rstrip() + "\n"
                self.tools.write(f_path, content)
                self._log(f"Wrote: {f_path}")

            # Remove any top-level tests/ directory if present (cleanup)
            tests_dir = self.repo / 'tests'
            if tests_dir.exists() and tests_dir.is_dir():
                try:
                    shutil.rmtree(tests_dir)
                    self._log("Removed top-level tests/ directory as requested.")
                except Exception as e:
                    self._log(f"Failed to remove tests/ directory: {e}")

            return RunResult(True, f"Scaffolded project with {len(file_blocks)} files.")

        # Fallback: single-module output
        self.tools.write(module_path, final_code)
        return RunResult(True, f"Wrote module: {module_path}")

    def commit_and_push(self, message: str, push: bool) -> RunResult:
        ok, out = self.tools.git_commit(message)
        if not ok:
            return RunResult(False, out)

        if push:
            ok2, out2 = self.tools.git_push()
            if not ok2:
                return RunResult(False, "Commit succeeded, but push failed:\n" + out2)
            return RunResult(True, "Commit and push succeeded.")

        return RunResult(True, "Commit succeeded.")

    def list_available_prompts(self) -> dict[str, list[str]]:
        """List all available prompt tasks and their variants."""
        tasks = self.prompt_manager.list_available_tasks()
        result = {}
        for task in tasks:
            result[task] = self.prompt_manager.list_variants(task)
        return result
