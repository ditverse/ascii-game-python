#!/usr/bin/env python3
"""
Terminal Pong - CLI-Based Multiplayer Game
Network Programming Final Project

A real-time multiplayer Pong game running entirely in CLI/Terminal using ASCII graphics.
Uses Host-Client architecture over TCP sockets.
Features: Chat Lobby, Real-time gameplay, ASCII UI
"""

import time

from input_handler import clear_screen, restore_terminal
from server import GameServer
from client import GameClient


def show_menu():
    """Display main menu."""
    clear_screen()
    print("""
+==============================================================+
|                                                              |
|              TERMINAL PONG                                   |
|              CLI-Based Multiplayer Game                      |
|              with Chat Lobby                                 |
|                                                              |
+==============================================================+
|                                                              |
|                    [1] Host Game (Server)                    |
|                    [2] Join Game (Client)                    |
|                    [Q] Quit                                  |
|                                                              |
+==============================================================+
    """)


def host_game():
    """Start as host."""
    clear_screen()
    print("\n[HOST MODE] Starting server...")
    
    server = GameServer()
    local_ip = server.start()
    
    time.sleep(0.5)
    client = GameClient()
    if client.connect("127.0.0.1"):
        client.run()
        client.close()
    
    server.stop()
    restore_terminal()


def join_game():
    """Join as guest."""
    clear_screen()
    print("\n[JOIN MODE]")
    
    host_ip = input("Enter Host IP Address: ").strip()
    if not host_ip:
        print("Invalid IP address!")
        time.sleep(2)
        return
    
    client = GameClient()
    if client.connect(host_ip):
        client.run()
        client.close()
    else:
        time.sleep(2)
    
    restore_terminal()


def main():
    """Main entry point."""
    while True:
        show_menu()
        choice = input("\n  Select option: ").strip().upper()
        
        if choice == '1':
            host_game()
        elif choice == '2':
            join_game()
        elif choice == 'Q':
            clear_screen()
            print("\nThank you for playing Terminal Pong!\n")
            break
        else:
            print("Invalid option!")
            time.sleep(1)


if __name__ == "__main__":
    main()
