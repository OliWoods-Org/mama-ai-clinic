#!/usr/bin/env bash
# Benchmark LLM inference speed on this device.
# Run this on the Pi to verify acceptable performance.

set -euo pipefail

API_URL="${LLAMA_API_URL:-http://127.0.0.1:8081}"

echo "=== Pi AI Clinic Inference Benchmark ==="
echo "Target: ${API_URL}"
echo ""

# Check server is running
if ! curl -s "${API_URL}/health" >/dev/null 2>&1; then
    echo "[ERROR] llama-server not reachable at ${API_URL}"
    echo "Start it with: systemctl start llama-server"
    exit 1
fi

# System info
echo "--- System Info ---"
if [ -f /proc/cpuinfo ]; then
    grep -m1 "model name" /proc/cpuinfo || echo "CPU: $(uname -m)"
fi
free -h | head -2
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    echo "CPU Temp: $((TEMP / 1000))C"
fi
echo ""

# Benchmark: simple medical query
echo "--- Benchmark: Clinical Query ---"
PROMPT="A 2-year-old child has had diarrhea for 3 days with no blood in stool. The child is drinking eagerly. What is the IMNCI classification?"

START=$(date +%s%N)
RESPONSE=$(curl -s "${API_URL}/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"local\",
        \"messages\": [{\"role\": \"user\", \"content\": \"${PROMPT}\"}],
        \"max_tokens\": 200,
        \"temperature\": 0.3
    }")
END=$(date +%s%N)

ELAPSED_MS=$(( (END - START) / 1000000 ))
TOKENS=$(echo "${RESPONSE}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('usage',{}).get('completion_tokens', 'N/A'))" 2>/dev/null || echo "N/A")

echo "Prompt: ${PROMPT:0:80}..."
echo "Time: ${ELAPSED_MS}ms"
echo "Completion tokens: ${TOKENS}"
if [ "${TOKENS}" != "N/A" ] && [ "${ELAPSED_MS}" -gt 0 ]; then
    TPS=$(python3 -c "print(f'{${TOKENS} / (${ELAPSED_MS} / 1000):.1f}')" 2>/dev/null || echo "N/A")
    echo "Tokens/sec: ${TPS}"

    MIN_TPS=5
    if python3 -c "exit(0 if ${TPS} >= ${MIN_TPS} else 1)" 2>/dev/null; then
        echo "[PASS] Performance is acceptable (>= ${MIN_TPS} tok/s)"
    else
        echo "[WARN] Performance below ${MIN_TPS} tok/s -- check active cooler and thermal throttling"
    fi
fi

echo ""
echo "--- Benchmark Complete ---"
