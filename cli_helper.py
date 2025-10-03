import time
import os
import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.console import Group
from rich.spinner import Spinner
from rich.box import SIMPLE

# Twitter ASCII Art
LOGO = """               
              ..=                     
              %%%                     
            .*%%%%                 
        +..%%%%%%%                
      .*%=.#%%%%%%%%                 
      %%%%=%%%%%%%%%%   *   ████████╗██╗    ██╗███████╗███████╗████████╗███████╗██╗██████╗ ███████╗   
  ..%%%%%%%%%%%%%%%%%+=%:   ╚══██╔══╝██║    ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██║██╔══██╗██╔════╝   
  .+%%%%%%%%%%.-%%%%%%%%%      ██║   ██║ █╗ ██║█████╗  █████╗     ██║   █████╗  ██║██████╔╝█████╗    
  .#%%%%%%%%%=. .%+%%%%%%%     ██║   ██║███╗██║██╔══╝  ██╔══╝     ██║   ██╔══╝  ██║██╔══██╗██╔══╝   
  .#%%%%%%*%*.   .:.%%%%%%#    ██║   ╚███╔███╔╝███████╗███████╗   ██║   ██║     ██║██║  ██║███████╗  
  .=%%%%%%.-         %%%%%#    ╚═╝    ╚══╝╚══╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝  
  ..#%%%%            %%%%%:            
      +%%%            %%%%:            
      ..*%=         .+%%=                                               

                    
"""

LOGO_TEXT_ONLY = """               
████████╗██╗    ██╗███████╗███████╗████████╗███████╗██╗██████╗ ███████╗
╚══██╔══╝██║    ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██║██╔══██╗██╔════╝
   ██║   ██║ █╗ ██║█████╗  █████╗     ██║   █████╗  ██║██████╔╝█████╗  
   ██║   ██║███╗██║██╔══╝  ██╔══╝     ██║   ██╔══╝  ██║██╔══██╗██╔══╝  
   ██║   ╚███╔███╔╝███████╗███████╗   ██║   ██║     ██║██║  ██║███████╗
   ╚═╝    ╚══╝╚══╝ ╚══════╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝
                                                                                                                                       
"""
LOGO_FIRE_ONLY = """               
              ..=                     
              %%%                     
            .*%%%%                 
        +..%%%%%%%                
      .*%=.#%%%%%%%%                 
      %%%%=%%%%%%%%%%   *     
  ..%%%%%%%%%%%%%%%%%+=%:  
  .+%%%%%%%%%%.-%%%%%%%%%  
  .#%%%%%%%%%=. .%+%%%%%%% 
  .#%%%%%%*%*.   .:.%%%%%%#   
  .=%%%%%%.-         %%%%%#   
  ..#%%%%            %%%%%: 
      +%%%            %%%%: 
      ..*%=         .+%%=   

                    
"""


class RichCLI:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.content_panels = []
        self.setup_layout()

    def setup_layout(self):
        """Setup the main layout structure with fixed header"""
        self.layout.split_column(
            Layout(name="header", size=18), Layout(name="main", ratio=1)
        )
        # Set the fixed header that never changes
        self.layout["header"].update(self.create_header())

    def create_header(self):
        """Create the fixed header with Twitter logo"""
        if os.get_terminal_size().columns < 80:
            return Panel(
                Align.center(Text(LOGO_FIRE_ONLY, style="bold dark-orange3")),
                style="bold orange3",
                padding=(0, 0),
                box=SIMPLE,
            )
        elif os.get_terminal_size().columns < 120:
            return Panel(
                Align.center(Text(LOGO_FIRE_ONLY, style="bold dark-orange3")),
                style="bold orange3",
                padding=(0, 0),
                box=SIMPLE,
            )
        else:
            return Panel(
                Align.center(Text(LOGO, style="bold dark-oranage3")),
                style="bold orange3",
                padding=(0, 0),
                box=SIMPLE,
            )

    def add_content_panel(self, panel):
        """Add a content panel to the scrollable main area"""
        self.content_panels.append(panel)
        self.update_main_content()

    def update_main_content(self):
        """Update the main content area with all panels"""
        if self.content_panels:
            self.layout["main"].update(Group(*self.content_panels))
        else:
            self.layout["main"].update(Panel("Ready to start   ", style="dim"))

    def clear_content(self):
        """Clear all content panels but keep the header"""
        self.content_panels = []
        self.update_main_content()

    async def run_with_spinner(
        self,
        coro,
        agent_name: str,
        description: str,
        color: str = "cyan",
        live_display=None,
    ):
        """Run a coroutine with a real animated spinner in the main area"""
        result = None
        error = None

        if live_display:
            # Create a spinner object
            spinner = Spinner("dots", style=color)
            spinner_panel = None

            # Create task to update spinner
            async def update_spinner():
                start_time = time.time()
                while True:
                    try:
                        # Update spinner frame
                        spinner_text = Text()
                        spinner_text.append(
                            str(spinner.render(time.time() - start_time)), style=color
                        )
                        spinner_text.append(
                            Text.from_markup(
                                f" [bold {color}]{agent_name}[/bold {color}]: {description}"
                            )
                        )

                        # Create new spinner panel
                        new_spinner_panel = Panel(
                            spinner_text,
                            style=color,
                            padding=(1, 2),
                        )

                        # Replace old spinner panel
                        nonlocal spinner_panel
                        if spinner_panel and spinner_panel in self.content_panels:
                            idx = self.content_panels.index(spinner_panel)
                            self.content_panels[idx] = new_spinner_panel
                        else:
                            self.content_panels.append(new_spinner_panel)

                        spinner_panel = new_spinner_panel
                        self.update_main_content()
                        live_display.refresh()

                        await asyncio.sleep(0.1)  # Update 10 times per second
                    except asyncio.CancelledError:
                        break

            # Start spinner task
            spinner_task = asyncio.create_task(update_spinner())

            try:
                result = await coro
            except Exception as e:
                error = e
            finally:
                # Stop spinner
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass

                # Remove spinner panel after completion
                if spinner_panel and spinner_panel in self.content_panels:
                    self.content_panels.remove(spinner_panel)
                    self.update_main_content()
        else:
            # Fallback without live display
            try:
                result = await coro
            except Exception as e:
                error = e

        return result, error
