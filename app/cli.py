import argparse
from rich.console import Console

from agent.orchestrator import Orchestrator

console = Console()


def main_cli() -> None:
    parser = argparse.ArgumentParser(description="CSDN Network / Cloudhydra Agent (Phase-1)")
    parser.add_argument(
        "question",
        nargs="*",
        help="Question for the agent (if empty, you will be prompted)",
    )
    args = parser.parse_args()

    if args.question:
        question = " ".join(args.question)
    else:
        question = console.input("[bold cyan]Ask your CSDN Agent a question:[/bold cyan] ")

    orch = Orchestrator()
    with console.status("[green]Thinking...[/green]"):
        answer = orch.route(question)

    console.print("\n[bold magenta]Agent:[/bold magenta]")
    console.print(answer)
