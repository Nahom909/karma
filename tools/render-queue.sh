#!/bin/bash
# Rendert alle Szenen nacheinander (wartet auf einen bereits laufenden Classic-Render).
cd "$(dirname "$0")/.."
while pgrep -f "pipeline.py classic" >/dev/null; do sleep 20; done
for s in "$@"; do
  echo "== $s $(date +%H:%M)" >> _work/logs/queue.log
  nice -n 5 python3 tools/blender/pipeline.py "$s" > "_work/logs/$s.log" 2>&1
  grep PIPELINE_DONE "_work/logs/$s.log" >> _work/logs/queue.log || echo "FEHLER $s" >> _work/logs/queue.log
done
echo "== fertig $(date +%H:%M)" >> _work/logs/queue.log
