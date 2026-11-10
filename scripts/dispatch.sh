#!/usr/bin/env bash
# Trigger a workflow on main, wait for it, then pull. Usage: scripts/dispatch.sh <workflow.yml>
set -u
R=chkoh89/macro-momentum
before=$(gh api "repos/$R/actions/runs?per_page=1" --jq '.workflow_runs[0].id // 0')
gh api -X POST "repos/$R/actions/workflows/$1/dispatches" -f ref=main
for i in $(seq 1 20); do id=$(gh api "repos/$R/actions/runs?per_page=1" --jq '.workflow_runs[0].id // 0'); [ "$id" != "$before" ] && break; sleep 3; done
for i in $(seq 1 60); do s=$(gh api "repos/$R/actions/runs/$id" --jq '[.status,.conclusion]|@tsv'); case "$s" in completed*) break;; esac; sleep 10; done
echo "run $id: $s"
gh api "repos/$R/actions/runs/$id/jobs" --jq '.jobs[].steps[] | select(.conclusion!="success" and .conclusion!="skipped") | [.name,.conclusion]|@tsv'
git pull -q --rebase origin main
