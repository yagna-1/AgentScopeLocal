"""
Terminal UI for AgentScope - Beautiful Rich Output

Provides stunning terminal visualization with modern aesthetics.
"""
import threading
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, HEAVY, DOUBLE
from rich.style import Style


class TerminalUI:
    """
    Beautiful Rich terminal interface for AgentScope.
    
    Modern design with vibrant colors and clean layout.
    """
    
    # Modern color palette
    COLORS = {
        'primary': '#00d9ff',      # Bright cyan
        'success': '#00ff87',      # Bright green
        'warning': '#ffaf00',      # Bright orange
        'error': '#ff5f87',        # Bright pink
        'info': '#af87ff',         # Bright purple
        'accent': '#ffff00',       # Bright yellow
        'dim': '#6c7086',          # Muted gray
        'highlight': '#f5c2e7',    # Light pink
    }
    
    def __init__(self):
        self.console = Console()
        self.active_spans: Dict[str, Dict[str, Any]] = {}
        self.completed_spans: List[Dict[str, Any]] = []
        self.trace_tree: Dict[str, List] = defaultdict(list)
        self._running = False
        self._lock = threading.Lock()
    
    def start(self):
        """Start the terminal UI with stunning header."""
        if self._running:
            return
        
        self._running = True
        
        # Create beautiful ASCII art header
        header_text = Text()
        header_text.append("╔═══════════════════════════════════════════════════════════╗\n", style="bold cyan")
        header_text.append("║  ", style="bold cyan")
        header_text.append("🕵️  AgentScope Local", style="bold #00d9ff")
        header_text.append(" " * 35, style="bold cyan")
        header_text.append("║\n", style="bold cyan")
        header_text.append("╠═══════════════════════════════════════════════════════════╣\n", style="bold cyan")
        header_text.append("║  ", style="bold cyan")
        header_text.append("🎯 Terminal Mode", style="#af87ff")
        header_text.append(" " * 10, style="bold cyan")
        header_text.append("│", style="#6c7086")
        header_text.append("  📊 Live Trace Visualization", style="#ffaf00")
        header_text.append("    ║\n", style="bold cyan")
        header_text.append("╠═══════════════════════════════════════════════════════════╣\n", style="bold cyan")
        header_text.append("║  ", style="bold cyan")
        header_text.append("✨ Performance", style="#00ff87")
        header_text.append(" │ ", style="#6c7086")
        header_text.append("🔍 RAG Debug", style="#f5c2e7")
        header_text.append(" │ ", style="#6c7086")
        header_text.append("⚡ Streaming", style="#ffff00")
        header_text.append(" │ ", style="#6c7086")
        header_text.append("💻 Resources", style="#ff5f87")
        header_text.append("  ║\n", style="bold cyan")
        header_text.append("╚═══════════════════════════════════════════════════════════╝", style="bold cyan")
        
        self.console.print()
        self.console.print(header_text)
        self.console.print()
    
    def stop(self):
        """Stop the terminal UI with beautiful summary."""
        if not self._running:
            return
        
        self._running = False
        
        # Print stunning summary
        self.console.print()
        self._print_session_summary()
        self.console.print()
    
    def _print_session_summary(self):
        """Print beautiful session summary with gradients."""
        total_spans = len(self.completed_spans)
        llm_spans = [s for s in self.completed_spans if self._is_llm_span(s.get('name', ''), s.get('attributes', {}))]
        
        # Create gradient summary table
        table = Table(
            title="[bold #00d9ff]📊 Session Summary[/bold #00d9ff]",
            box=DOUBLE,
            border_style="#af87ff",
            header_style="bold #ffaf00"
        )
        table.add_column("Metric", style="bold #00d9ff", justify="left", no_wrap=True)
        table.add_column("Value", style="bold #00ff87", justify="right", no_wrap=True)
        
        table.add_row("📦 Total Spans", f"[#ffff00]{total_spans}[/#ffff00]")
        table.add_row("🤖 LLM Calls", f"[#00ff87]{len(llm_spans)}[/#00ff87]")
        
        if llm_spans:
            total_tokens = sum(s.get('attributes', {}).get('gen_ai.usage.total_tokens', 0) for s in llm_spans)
            table.add_row("💬 Total Tokens", f"[#af87ff]{total_tokens:,}[/#af87ff]")
        
        self.console.print(table)
        self.console.print()
        
        # Beautiful tip
        tip_panel = Panel(
            "[#6c7086]💡 Tip: Run [bold #00d9ff]ag.web.open()[/bold #00d9ff] to explore traces in your browser![/#6c7086]",
            border_style="#f5c2e7",
            box=ROUNDED
        )
        self.console.print(tip_panel)
    
    def on_span_start(self, span):
        """Called when a span starts - show beautiful notification."""
        with self._lock:
            span_id = getattr(span, 'span_id', id(span))
            parent_id = getattr(span.parent, 'span_id', None) if hasattr(span, 'parent') and span.parent else None
            
            self.active_spans[span_id] = {
                'name': span.name,
                'start_time': datetime.now(),
                'parent_id': parent_id,
                'attributes': {}
            }
            
            self.trace_tree[parent_id].append(span_id)
        
        # Beautiful span start with colors
        indent = self._get_indent_level(span_id)
        icon = self._get_span_icon(span.name)
        color = self._get_span_color(span.name)
        
        self.console.print(f"{'  ' * indent}{icon} [bold {color}]{span.name}[/bold {color}]")
    
    def on_span_end(self, span):
        """Called when a span ends - show stunning metrics."""
        span_id = getattr(span, 'span_id', id(span))
        
        with self._lock:
            if span_id in self.active_spans:
                span_data = self.active_spans.pop(span_id)
                span_data['end_time'] = datetime.now()
                span_data['attributes'] = dict(span.attributes) if hasattr(span, 'attributes') else {}
                span_data['span'] = span
                self.completed_spans.append(span_data)
        
        attrs = dict(span.attributes) if hasattr(span, 'attributes') else {}
        indent = self._get_indent_level(span_id)
        prefix = '  ' * indent
        
        if self._is_llm_span(span.name, attrs):
            self._print_llm_beautiful(span, attrs, prefix)
        elif self._is_rag_span(span.name, attrs):
            self._print_rag_beautiful(span, attrs, prefix)
        else:
            self._print_generic_beautiful(span, attrs, prefix)
        
        self.console.print()
    
    def _get_indent_level(self, span_id) -> int:
        """Calculate indentation level."""
        level = 0
        for parent_id, children in self.trace_tree.items():
            if span_id in children:
                if parent_id is not None:
                    level = self._get_indent_level(parent_id) + 1
                break
        return level
    
    def _print_llm_beautiful(self, span, attrs: Dict, prefix: str):
        """Print stunning LLM metrics with modern design."""
        # Extract metrics
        model = attrs.get('gen_ai.request.model', 'unknown')
        provider = attrs.get('gen_ai.system', 'unknown')
        
        prompt_tokens = attrs.get('gen_ai.usage.prompt_tokens', 0)
        completion_tokens = attrs.get('gen_ai.usage.completion_tokens', 0)
        total_tokens = attrs.get('gen_ai.usage.total_tokens', 0)
        
        ttft = attrs.get('llm.ttft_ms')
        tps = attrs.get('llm.tokens_per_second')
        gen_time = attrs.get('llm.generation_time_ms')
        
        temperature = attrs.get('gen_ai.request.temperature')
        max_tokens = attrs.get('gen_ai.request.max_tokens')
        context_window = attrs.get('gen_ai.model.context_window')
        
        cpu = attrs.get('system.cpu_percent')
        memory = attrs.get('system.memory_mb')
        
        streaming = attrs.get('llm.streaming.enabled', False)
        
        # Create beautiful gradient table
        table = Table(
            box=DOUBLE,
            border_style="#00d9ff",
            show_header=False,
            padding=(0, 2),
            style="on #0a0e14"
        )
        table.add_column("", style="bold #af87ff", justify="right", width=18)
        table.add_column("", style="bold white")
        
        # Header
        table.add_row("", "")
        table.add_row("[bold #00d9ff]📡 LLM CALL", "")
        table.add_row("", "")
        
        # Model info with gradient
        table.add_row("🔷 Provider", f"[#ffaf00]{provider.upper()}[/#ffaf00]")
        table.add_row("🤖 Model", f"[#00ff87]{model}[/#00ff87]")
        
        # Tokens with color coding
        if total_tokens:
            token_visual = self._create_token_visual(prompt_tokens, completion_tokens)
            table.add_row("💬 Tokens", token_visual)
        
        # Performance metrics with color coding
        if ttft:
            ttft_color = self._get_metric_color(ttft, [500, 1500, 3000])
            table.add_row("⚡ TTFT", f"[{ttft_color}]{ttft:.0f}ms[/{ttft_color}]")
        
        if tps:
            tps_color = "#00ff87" if tps > 50 else "#ffaf00" if tps > 20 else "#ff5f87"
            table.add_row("🚀 Speed", f"[{tps_color}]{tps:.1f} tok/s[/{tps_color}]")
        
        if gen_time:
            table.add_row("⏱️  Duration", f"[#af87ff]{gen_time:.0f}ms[/#af87ff]")
        
        # Configuration
        if temperature is not None or max_tokens:
            table.add_row("", "")
            table.add_row("[#6c7086]⚙️  CONFIG", "")
        
        if temperature is not None:
            temp_bar = self._create_mini_bar(temperature, max_val=2.0)
            table.add_row("  🌡️  Temp", f"[#ffaf00]{temp_bar} {temperature}[/#ffaf00]")
        
        if max_tokens:
            table.add_row("  📝 Max", f"[#6c7086]{max_tokens}[/#6c7086]")
        
        # Context window with beautiful progress bar
        if context_window and total_tokens:
            usage_pct = (total_tokens / context_window) * 100
            ctx_bar = self._create_gradient_bar(usage_pct)
            ctx_color = self._get_metric_color(usage_pct, [50, 75, 90])
            table.add_row("  📊 Context", f"{ctx_bar} [{ctx_color}]{usage_pct:.0f}%[/{ctx_color}]")
        
        # Resources
        if cpu is not None or memory is not None:
            table.add_row("", "")
            table.add_row("[#6c7086]💻 RESOURCES", "")
        
        if cpu is not None:
            cpu_bar = self._create_gradient_bar(cpu)
            cpu_color = self._get_metric_color(cpu, [50, 75, 90])
            table.add_row("  ⚙️  CPU", f"{cpu_bar} [{cpu_color}]{cpu:.0f}%[/{cpu_color}]")
        
        if memory is not None:
            table.add_row("  🧠 RAM", f"[#af87ff]{memory:.0f} MB[/#af87ff]")
        
        # Streaming badge
        if streaming:
            table.add_row("", "")
            table.add_row("  ⚡ STREAMING", "[bold #ffff00]ENABLED[/bold #ffff00]")
        
        # Render in beautiful panel
        panel = Panel(
            table,
            border_style="bold #00d9ff",
            padding=(1, 2),
            box=DOUBLE
        )
        
        from io import StringIO
        from rich.console import Console as TempConsole
        
        temp_console = TempConsole(file=StringIO(), width=70)
        temp_console.print(panel)
        output = temp_console.file.getvalue()
        
        for line in output.split('\n'):
            if line.strip():
                self.console.print(f"{prefix}{line}")
        
        # Success indicator
        self.console.print(f"{prefix}  [bold #00ff87]✓ COMPLETE[/bold #00ff87]")
    
    def _print_rag_beautiful(self, span, attrs: Dict, prefix: str):
        """Print beautiful RAG information."""
        vector_type = attrs.get('vector_type', 'query')
        dimension = attrs.get('vector_dimension')
        
        table = Table(box=DOUBLE, border_style="#f5c2e7", show_header=False, padding=(0, 2))
        table.add_column("", style="bold #af87ff", justify="right", width=15)
        table.add_column("", style="bold white")
        
        table.add_row("[bold #f5c2e7]🔍 RAG", "")
        table.add_row("", "")
        table.add_row("📌 Type", f"[#ffaf00]{vector_type.upper()}[/#ffaf00]")
        
        if dimension:
            table.add_row("📏 Dims", f"[#00ff87]{dimension}[/#00ff87]")
        
        panel = Panel(table, border_style="#f5c2e7", padding=(1, 2), box=DOUBLE)
        
        from io import StringIO
        from rich.console import Console as TempConsole
        
        temp_console = TempConsole(file=StringIO(), width=50)
        temp_console.print(panel)
        output = temp_console.file.getvalue()
        
        for line in output.split('\n'):
            if line.strip():
                self.console.print(f"{prefix}{line}")
        
        self.console.print(f"{prefix}  [bold #00ff87]✓ COMPLETE[/bold #00ff87]")
    
    def _print_generic_beautiful(self, span, attrs: Dict, prefix: str):
        """Print generic span with style."""
        duration = self._calculate_duration(span)
        
        if duration:
            self.console.print(f"{prefix}  [bold #00ff87]✓[/bold #00ff87] [#6c7086]{duration:.0f}ms[/#6c7086]")
        else:
            self.console.print(f"{prefix}  [bold #00ff87]✓ COMPLETE[/bold #00ff87]")
    
    def _create_token_visual(self, prompt: int, completion: int) -> str:
        """Create beautiful token visualization."""
        total = prompt + completion
        return f"[#af87ff]{prompt}[/#af87ff] [#6c7086]→[/#6c7086] [#00ff87]{completion}[/#00ff87] [#6c7086]([/#6c7086][bold #ffaf00]{total}[/bold #ffaf00][#6c7086] total)[/#6c7086]"
    
    def _create_gradient_bar(self, percentage: float, width: int = 15) -> str:
        """Create beautiful gradient progress bar."""
        filled = int((percentage / 100) * width)
        bar = ""
        
        for i in range(width):
            if i < filled:
                # Gradient from green to yellow to red
                if percentage < 50:
                    bar += "[#00ff87]█[/#00ff87]"
                elif percentage < 75:
                    bar += "[#ffaf00]█[/#ffaf00]"
                else:
                    bar += "[#ff5f87]█[/#ff5f87]"
            else:
                bar += "[#6c7086]░[/#6c7086]"
        
        return bar
    
    def _create_mini_bar(self, value: float, max_val: float = 1.0, width: int = 10) -> str:
        """Create mini bar for small values."""
        percentage = (value / max_val) * 100
        filled = int((percentage / 100) * width)
        return "[#ffaf00]" + "▮" * filled + "[/#ffaf00]" + "[#6c7086]" + "▯" * (width - filled) + "[/#6c7086]"
    
    def _get_metric_color(self, value: float, thresholds: list) -> str:
        """Get color based on metric thresholds."""
        if value < thresholds[0]:
            return "#00ff87"  # Green
        elif value < thresholds[1]:
            return "#ffaf00"  # Orange
        elif value < thresholds[2]:
            return "#ff5f87"  # Pink/Red
        else:
            return "#ff0000"  # Red
    
    def _is_llm_span(self, name: str, attrs: Dict) -> bool:
        """Check if span is LLM call."""
        return (
            'gen_ai.system' in attrs or
            'llm' in name.lower() or
            'chat' in name.lower()
        )
    
    def _is_rag_span(self, name: str, attrs: Dict) -> bool:
        """Check if span is RAG operation."""
        return (
            'rag' in name.lower() or
            'retrieval' in name.lower() or
            'embedding' in name.lower() or
            'vector_type' in attrs
        )
    
    def _calculate_duration(self, span) -> Optional[float]:
        """Calculate span duration in milliseconds."""
        if hasattr(span, 'start_time') and hasattr(span, 'end_time'):
            return (span.end_time - span.start_time) / 1_000_000
        return None
    
    def _get_span_icon(self, name: str) -> str:
        """Get vibrant icon for span type."""
        name_lower = name.lower()
        
        if 'llm' in name_lower or 'chat' in name_lower:
            return '🤖'
        elif 'rag' in name_lower or 'retrieval' in name_lower:
            return '🔍'
        elif 'embedding' in name_lower:
            return '📊'
        else:
            return '▶️'
    
    def _get_span_color(self, name: str) -> str:
        """Get color for span type."""
        name_lower = name.lower()
        
        if 'llm' in name_lower or 'chat' in name_lower:
            return "#00d9ff"
        elif 'rag' in name_lower or 'retrieval' in name_lower:
            return "#f5c2e7"
        elif 'embedding' in name_lower:
            return "#af87ff"
        else:
            return "#ffaf00"
    
    def print_streaming_chunk(self, chunk: str):
        """Print streaming chunk with style."""
        self.console.print(f"[#00d9ff]{chunk}[/#00d9ff]", end="", markup=False)
