#!/usr/bin/env python3

import asyncio
import json
from datetime import datetime
import time

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

from cli_helper import RichCLI

from agents.find_trend import find_trend
from agents.content_generator import ContentGenerator
from agents.image_generator import generate_image
from agents.twitter_poster import post_to_twitter

# Initialize rich console
console = Console()


# Initialize CLI
cli = RichCLI()


async def main():
    """Main orchestration function with fixed header Live display"""
    # Clear screen and set up Live display with fixed header
    console.clear()

    with Live(cli.layout, console=console, refresh_per_second=4, screen=True) as live:
        try:
            # Add initial status
            startup_panel = Panel(
                "🚀 [bold orange3]Starting Automated Trend-to-Tweet Pipeline[/bold orange3]",
                style="orange3",
                padding=(1, 2),
            )
            cli.add_content_panel(startup_panel)
            live.refresh()

            # Step 1: Find trending topics
            trend_data, error = await cli.run_with_spinner(
                find_trend(),
                "Trend Finder",
                "Analyzing trending topics using Android automation...",
                "bright_magenta",
                live,
            )

            if error or not trend_data:
                error_panel = Panel(
                    "❌ [bold red]Failed to find trending topics. Exiting.[/bold red]",
                    style="red",
                )
                cli.add_content_panel(error_panel)
                live.refresh()
                return

            success_panel = Panel(
                f"✅ [bold green]Found trending topic:[/bold green] [yellow]{trend_data.get('trending_topic', 'Unknown')}[/yellow]",
                style="green",
            )
            cli.add_content_panel(success_panel)
            live.refresh()

            # Step 2: Generate content using Gemini API
            content_generator = ContentGenerator()
            generated_content, error = await cli.run_with_spinner(
                content_generator.generate_content_from_trend(trend_data),
                "Content Generator",
                "Creating Twitter post and image prompt with AI...",
                "dodger_blue1",
                live,
            )

            if error or not generated_content:
                error_panel = Panel(
                    f"❌ [bold red]Content generation failed: {error}[/bold red]",
                    style="red",
                )
                cli.add_content_panel(error_panel)
                live.refresh()
                return

            twitter_post = generated_content["twitter_post"]
            image_prompt = generated_content["image_prompt"]

            # Display generated content
            content_panel = Panel(
                f"[bold blue]Twitter Post:[/bold blue]\n[yellow]{twitter_post}[/yellow]\n\n",
                title="📝 Generated Content",
                style="dodger_blue1",
            )
            cli.add_content_panel(content_panel)
            live.refresh()

            # Step 3: Generate image using Gemini
            image_result, error = await cli.run_with_spinner(
                generate_image(image_prompt),
                "Image Generator",
                "Creating visual content with AI...",
                "bright_green",
                live,
            )

            if error or not image_result:
                warning_panel = Panel(
                    f"⚠️ [bold yellow]Image generation failed: {error}[/bold yellow]",
                    style="yellow",
                )
                cli.add_content_panel(warning_panel)
                image_success = False
            else:
                image_success = image_result.get("success", False)

            if image_success:
                success_panel = Panel(
                    "✅ [bold green]Image generated and downloaded successfully[/bold green]",
                    style="green",
                )
                cli.add_content_panel(success_panel)
            else:
                warning_panel = Panel(
                    "⚠️ [bold yellow]Image generation failed, will post without image[/bold yellow]",
                    style="yellow",
                )
                cli.add_content_panel(warning_panel)

            live.refresh()

            # Step 4: Post to Twitter
            post_result, error = await cli.run_with_spinner(
                post_to_twitter(twitter_post, has_image=image_success),
                "Twitter Poster",
                "Publishing content to Twitter...",
                "cyan",
                live,
            )

            if error or not post_result:
                error_panel = Panel(
                    f"❌ [bold red]Twitter posting failed: {error}[/bold red]",
                    style="red",
                )
                cli.add_content_panel(error_panel)
                post_success = False
            else:
                post_success = post_result.get("success", False)

            if post_success:
                success_panel = Panel(
                    "✅ [bold green]Successfully posted to Twitter![/bold green]",
                    style="green",
                )
                cli.add_content_panel(success_panel)
            else:
                error_panel = Panel(
                    "❌ [bold red]Failed to post to Twitter[/bold red]", style="red"
                )
                cli.add_content_panel(error_panel)

            live.refresh()

            # Execution Summary
            summary_text = Text()
            summary_text.append("📊 EXECUTION SUMMARY\n", style="bold white")
            summary_text.append("─" * 50 + "\n", style="dim white")
            summary_text.append("Trending Topic: ", style="bold white")
            summary_text.append(
                f"{trend_data.get('trending_topic', 'Unknown')}\n", style="yellow"
            )
            summary_text.append("Twitter Post: ", style="bold white")
            summary_text.append(f"{twitter_post}\n", style="cyan")
            summary_text.append("Image Generated: ", style="bold white")
            summary_text.append(
                f"{'Yes' if image_success else 'No'}\n",
                style="green" if image_success else "red",
            )
            summary_text.append("Posted to Twitter: ", style="bold white")
            summary_text.append(
                f"{'Yes' if post_success else 'No'}\n",
                style="green" if post_success else "red",
            )
            summary_text.append("Execution Time: ", style="bold white")
            summary_text.append(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim white"
            )

            summary_panel = Panel(
                summary_text, title="📊 Results", style="white", padding=(1, 2)
            )
            cli.add_content_panel(summary_panel)
            live.refresh()

            # Save execution log
            execution_log = {
                "timestamp": datetime.now().isoformat(),
                "trend_data": trend_data,
                "generated_content": generated_content,
                "image_generated": image_success,
                "twitter_posted": post_success,
                "twitter_post": twitter_post,
                "image_prompt": image_prompt,
            }

            with open("execution_log.json", "w") as f:
                json.dump(execution_log, f, indent=2)

            log_panel = Panel(
                "📝 [bold green]Execution log saved to execution_log.json[/bold green]",
                style="green",
            )
            cli.add_content_panel(log_panel)
            live.refresh()

        except KeyboardInterrupt:
            interrupt_panel = Panel(
                "⏹️ [bold yellow]Process interrupted by user[/bold yellow]",
                style="yellow",
            )
            cli.add_content_panel(interrupt_panel)
            live.refresh()
            raise
        except Exception as e:
            error_panel = Panel(
                f"❌ [bold red]Error during execution: {str(e)}[/bold red]", style="red"
            )
            cli.add_content_panel(error_panel)
            live.refresh()
            raise


if __name__ == "__main__":
    # Show startup info
    console.print(
        Panel(
            "[bold cyan]🤖 Automated Social Media Content Creation[/bold cyan]\n\n"
            "📱 Make sure your Android device is connected and ADB is enabled!\n"
            "🔑 Also ensure you have set your GEMINI_API_KEY in your .env file\n"
            "⚡ Press Ctrl+C anytime to stop the process",
            title="🚀 Setup Information",
            style="blue",
            padding=(1, 2),
        )
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(
            Panel(
                "⏹️ [bold yellow]Process interrupted by user[/bold yellow]",
                style="yellow",
            )
        )
    except Exception as e:
        console.print(
            Panel(
                f"💥 [bold red]Fatal error: {str(e)}[/bold red]\n"
                "[dim]Please check your setup and try again.[/dim]",
                style="red",
            )
        )
