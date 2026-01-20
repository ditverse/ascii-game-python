import os
import sys
import time
import threading


class InputHandler:
    """Thread-safe input handler for cross-platform keyboard input."""
    
    def __init__(self):
        self.current_key = None
        self.current_line = ""
        self.line_ready = False
        self.lock = threading.Lock()
        self.running = True
        self._old_settings = None
        self._thread = None
        self.mode = "key"  # "key" for single key, "line" for text input
        
    def start(self):
        """Start the input handler thread."""
        if os.name != 'nt':
            import termios
            try:
                self._old_settings = termios.tcgetattr(sys.stdin.fileno())
            except:
                pass
        
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the input handler and restore terminal."""
        self.running = False
        if os.name != 'nt' and self._old_settings:
            import termios
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except:
                pass
    
    def set_mode(self, mode):
        """Set input mode: 'key' or 'line'."""
        with self.lock:
            self.mode = mode
            self.current_line = ""
            self.line_ready = False
    
    def get_key(self):
        """Get the current key (thread-safe)."""
        with self.lock:
            key = self.current_key
            self.current_key = None
            return key
    
    def get_line(self):
        """Get completed line input."""
        with self.lock:
            if self.line_ready:
                line = self.current_line
                self.current_line = ""
                self.line_ready = False
                return line
            return None
    
    def get_partial_line(self):
        """Get current partial line being typed."""
        with self.lock:
            return self.current_line
    
    def _input_loop(self):
        """Background thread that reads keyboard input."""
        if os.name == 'nt':
            self._windows_input_loop()
        else:
            self._linux_input_loop()
    
    def _windows_input_loop(self):
        """Windows input loop using msvcrt."""
        import msvcrt
        while self.running:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    try:
                        key_char = key.decode('utf-8')
                        self._process_key(key_char)
                    except:
                        pass
                time.sleep(0.01)
            except:
                break
    
    def _linux_input_loop(self):
        """Linux input loop using raw terminal mode."""
        import tty
        import termios
        import select
        
        fd = sys.stdin.fileno()
        try:
            tty.setcbreak(fd)
            while self.running:
                try:
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        key = sys.stdin.read(1)
                        self._process_key(key)
                except:
                    break
        finally:
            if self._old_settings:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
                except:
                    pass
    
    def _process_key(self, key):
        """Process a key press based on current mode."""
        with self.lock:
            # Always set current_key for single-key reading
            self.current_key = key.upper()
            
            if self.mode == "line":
                # In line mode, also accumulate text for chat
                if key == '\r' or key == '\n':
                    self.line_ready = True
                elif key == '\x7f' or key == '\b':  # Backspace
                    self.current_line = self.current_line[:-1]
                elif key.isprintable() and key.upper() not in ['Q']:
                    # Don't add Q to chat line (it's quit command)
                    # TAB is handled separately
                    if len(self.current_line) < 40:
                        self.current_line += key


def clear_screen():
    """Clear the terminal screen."""
    print("\033[H\033[J", end="", flush=True)


def restore_terminal():
    """Restore terminal to normal mode."""
    if os.name != 'nt':
        os.system('stty sane')
