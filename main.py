import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from interview_coach import InterviewCoach
from pathlib import Path

console = Console()

def run_cli():
    # 1. Setup argparse to handle CLI inputs easily
    parser = argparse.ArgumentParser(description="AI Interview Coach")
    parser.add_argument("--job", "-j", help="Path to job description file")
    parser.add_argument("--type", "-t", default="technical", help="Interview type (technical, behavioral, system_design)")
    parser.add_argument("--level", "-l", default="senior", help="Position level (junior, mid, senior, staff)")
    parser.add_argument("--questions", "-q", type=int, default=5, help="Number of questions to ask")
    args = parser.parse_args()

    # 2. Present a nice header using Rich Panel
    console.print(Panel.fit(
        "[bold cyan]AI Interview Coach (Gemini Powered)[/bold cyan]\n"
        "Practice mock interviews with automated scoring and constructive feedback.",
        border_style="cyan"
    ))

    # 3. Initialize the core InterviewCoach instance
    console.print("[dim]Initializing Gemini models and chains...[/dim]")
    try:
        # Validate job description path if provided
        job_path = None
        if args.job:
            candidate = Path(args.job)
            if candidate.exists():
                job_path = str(candidate)
            else:
                # Try common project folders in case of typo
                filename = candidate.name
                alt_dirs = [Path("data/job_description"), Path("data/job_descriptions")]
                for d in alt_dirs:
                    alt = d / filename
                    if alt.exists():
                        job_path = str(alt)
                        break

                if job_path is None:
                    console.print(f"[bold red]Job description not found:[/bold red] {args.job}")
                    console.print("[yellow]Tip: place your JD under data/job_description/ or provide a valid path.[/yellow]")
                    sys.exit(1)

        coach = InterviewCoach(
            job_description_path=job_path,
            interview_type=args.type,
            level=args.level
        )
    except Exception as e:
        console.print(f"[bold red]Initialization Error:[/bold red] {e}")
        console.print("[yellow]Please ensure you have set GOOGLE_API_KEY in your .env file.[/yellow]")
        sys.exit(1)

    session_id = "cli_session"
    topics = ["Python fundamentals", "system design", "algorithms", "problem solving", "best practices"]

    # 4. Start the interview session
    welcome = coach.start_interview(session_id, topics[:args.questions])
    console.print(f"\n[bold green]Interviewer:[/bold green] {welcome}\n")

    # 5. Continuous Loop for the Q&A turns
    while True:
        try:
            answer = console.input("[bold blue]You:[/bold blue] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Interview ended early.[/yellow]")
            break

        # Let the candidate exit easily
        if answer.strip().lower() in ['quit', 'exit', 'q']:
            console.print("[yellow]Interview ended early.[/yellow]")
            break

        if not answer.strip():
            console.print("[yellow]Please provide an answer, or type 'q' to quit.[/yellow]")
            continue

        console.print("[dim]Evaluating your answer...[/dim]")
        
        # Submit the candidate's answer to the coach
        result = coach.submit_answer(session_id, answer)

        if "error" in result:
            console.print(f"[bold red]Error:[/bold red] {result['error']}")
            break

        # Display structured single-turn feedback
        feedback = result["feedback"]
        console.print(f"\n[dim]Score: {feedback.score}/10 - {feedback.understanding}[/dim]")

        # Check if the interview reached its maximum questions limit
        if result["is_complete"]:
            console.print("\n[bold green]Interview complete! Generating your comprehensive report...[/bold green]\n")

            # Generate final aggregated report
            report = coach.generate_report(session_id)

            # Display final report nicely inside a green Panel
            console.print(Panel(
                f"[bold]Overall Score: {report.overall_score}/10[/bold]\n"
                f"Recommendation: [cyan]{report.recommendation.upper()}[/cyan]\n\n"
                f"[bold]Summary:[/bold]\n{report.summary}\n\n"
                f"[green]Strengths:[/green]\n" +
                "\n".join(f"  • {s}" for s in report.strengths) + "\n\n"
                f"[yellow]Areas to Improve:[/yellow]\n" +
                "\n".join(f"  • {a}" for a in report.areas_to_improve) + "\n\n"
                f"[cyan]Suggested Topics to Study:[/cyan]\n" +
                "\n".join(f"  • {t}" for t in report.suggested_topics_to_study),
                title="[bold green]Final Interview Report[/bold green]",
                border_style="green"
            ))
            break

        # Show next question
        console.print(f"\n[bold green]Interviewer:[/bold green] {result['next_question']}\n")
        console.print(f"[dim]({result['questions_remaining']} questions remaining)[/dim]\n")

if __name__ == "__main__":
    run_cli()