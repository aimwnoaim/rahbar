#!/usr/bin/env bash
set -euo pipefail

context=${RAGOPS_CONTEXT:-ragops-dev}
k=(kubectl --context "$context" -n ragops)
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

run_job() {
  local name=$1 file=$2
  "${k[@]}" delete job "$name" --ignore-not-found
  "${k[@]}" apply -f "$file"
  if ! "${k[@]}" wait --for=condition=complete "job/$name" --timeout=40m; then
    "${k[@]}" logs "job/$name"
    return 1
  fi
  "${k[@]}" logs "job/$name"
}

"${k[@]}" get all,pvc,configmap
run_job eval k8s/eval-job.yaml

port=${RAGOPS_LOCAL_PORT:-18080}
"${k[@]}" port-forward svc/api "$port:8000" > /dev/null 2>&1 &
forward=$!
trap 'kill "$forward" 2>/dev/null || true' EXIT
curl --fail --silent --retry 10 --retry-connrefused "http://127.0.0.1:$port/healthz"
result=$(curl --fail --silent --max-time 240 -X POST "http://127.0.0.1:$port/query" \
  -H 'Content-Type: application/json' \
  -d '{"question":"How long can I borrow an audio recorder from the media desk?"}')
trace_id=$(python -c 'import json,sys; print(json.load(sys.stdin)["trace_id"])' <<< "$result")
"${k[@]}" exec deploy/api -- python -m ragops trace "$trace_id"

loader=$("${k[@]}" get pod -l app.kubernetes.io/name=inbox-loader -o jsonpath='{.items[0].metadata.name}')
"${k[@]}" exec "$loader" -- mkdir -p /data/demo-inbox
"${k[@]}" cp data/demo_batch/. "$loader:/data/demo-inbox"
"${k[@]}" delete job demo-ingest --ignore-not-found
"${k[@]}" create job demo-ingest --from=cronjob/ingest --dry-run=client -o json |
  python -c 'import json,sys; job=json.load(sys.stdin); job["spec"]["template"]["spec"]["containers"][0]["args"]=["--inbox","/data/demo-inbox","--out","/data/results"]; print(json.dumps(job))' |
  "${k[@]}" apply -f -
"${k[@]}" wait --for=condition=complete job/demo-ingest --timeout=5m
"${k[@]}" logs job/demo-ingest
