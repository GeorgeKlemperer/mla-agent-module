import anthropic
import subprocess
from pathlib import Path

client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file, or list the names in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, overwriting any existing content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_shell",
        "description": "Run a shell command and return its output. Use this to run tests, check git status, list files, etc.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
]

def read_file(path: str) -> str:
    target = Path(path)
    if target.is_dir():
        return "\n".join(p.name for p in target.iterdir())
    return target.read_text()

def write_file(path: str, content: str) -> str:
    Path(path).write_text(content)
    return f"Wrote {len(content)} characters to {path}"

def run_shell(command: str) -> str:
    print(f"\n[permission] The agent wants to run: {command}")
    if input("Allow? [y/N] ").strip().lower() != "y":
        return "Error: user denied permission to run command"
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout + result.stderr
    return f"Exit code: {result.returncode}\n{output}"

def run_tool(name: str, arguments: dict) -> str:
    try:
        if name == "read_file":
            return read_file(arguments["path"])
        if name == "write_file":
            return write_file(arguments["path"], arguments["content"])
        if name == "run_shell":
            return run_shell(arguments["command"])
        return f"Error: unknown tool '{name}'"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

def agent(prompt: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": prompt}]

    for turn in range(1, max_turns + 1):
        print(f"\n--- Turn {turn} ---")

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type == "text":
                print(f"[assistant] {block.text}")
            elif block.type == "tool_use":
                print(f"[tool call] {block.name}({block.input})")
                result = run_tool(block.name, block.input)
                is_error = result.startswith("Error:")
                print(f"[tool result] {result[:200]}{'...' if len(result) > 200 else ''}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                    "is_error": is_error,
                })

        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if b.type == "text"), "")
        if not tool_results:
            raise RuntimeError(f"Model stopped without tool calls: {response.stop_reason}")

        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Agent did not terminate within {max_turns} turns")

# agent("Add a docstring to the top of sample_project/calculator.py explaining what the module does.")
# agent("Run the tests in sample_project/ and tell me what's failing.")
# agent("Read sample_project/does_not_exist.py and summarise it.")
agent("""
The tests in sample_project/ are failing. Investigate what's wrong,
fix the code, and re-run the tests to confirm everything passes.
""")
