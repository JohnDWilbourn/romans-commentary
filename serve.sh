#!/bin/bash
# ============================================================
# ROMANS ROAD — LOCAL SERVER
# Run this to serve the commentary locally.
# Open the printed URL on any device on the same WiFi network.
# ============================================================

PORT=8000
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║         ROMANS ROAD — LOCAL SERVER       ║"
echo "  ╠══════════════════════════════════════════╣"
echo "  ║                                          ║"
echo "  ║  Laptop:  http://localhost:$PORT           ║"
echo "  ║  Phone:   http://$LOCAL_IP:$PORT      ║"
echo "  ║                                          ║"
echo "  ║  Both devices must be on the same WiFi. ║"
echo "  ║  Press Ctrl+C to stop the server.       ║"
echo "  ║                                          ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

cd "$DIR"
python3 -m http.server $PORT
