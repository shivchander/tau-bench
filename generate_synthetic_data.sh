#!/bin/bash

# Synthetic Data Generation Script for tau-bench
# Generates 30 tasks each for easy, medium, and hard difficulty levels

set -e  # Exit on any error

echo "🚀 Starting synthetic data generation for tau-bench..."
echo "Target: 30 easy + 30 medium + 30 hard = 90 total tasks"
echo ""

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    echo "Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p tau_bench/sdg

# # Generate and validate easy tasks (30 samples)
# echo "📝 Generating 30 easy tasks (1 action each)..."
# uv run python tau_bench/sdg/generate_user_actions.py \
#     --num-samples 30 \
#     --difficulty easy \
#     --max-concurrency 8 \
#     --output-file tau_bench/sdg/synthetic_tasks_easy

# echo "✅ Easy tasks generated!"
# echo ""

# echo "🔍 Validating easy task sequences..."
# uv run python tau_bench/sdg/validate_actions_simple.py \
#     --input-file tau_bench/sdg/synthetic_tasks_easy.json \
#     --output-file tau_bench/sdg/validated_tasks_easy.json

# echo "✅ Easy task validation completed!"
# echo ""

# Generate and validate medium tasks (30 samples)
echo "📝 Generating 30 medium tasks (2-5 actions each)..."
uv run python tau_bench/sdg/generate_user_actions.py \
    --num-samples 1000 \
    --difficulty medium \
    --max-concurrency 10 \
    --output-file tau_bench/sdg/synthetic_tasks_medium

echo "✅ Medium tasks generated!"
echo ""

echo "🔍 Validating medium task sequences..."
uv run python tau_bench/sdg/validate_actions_simple.py \
    --input-file tau_bench/sdg/synthetic_tasks_medium.json \
    --output-file tau_bench/sdg/validated_tasks_medium.json

echo "✅ Medium task validation completed!"
echo ""

# # Generate and validate hard tasks (30 samples)
# echo "📝 Generating 30 hard tasks (6-10 actions each)..."
# uv run python tau_bench/sdg/generate_user_actions.py \
#     --num-samples 30 \
#     --difficulty hard \
#     --max-concurrency 8 \
#     --output-file tau_bench/sdg/synthetic_tasks_hard

# echo "✅ Hard tasks generated!"
# echo ""

# echo "🔍 Validating hard task sequences..."
# uv run python tau_bench/sdg/validate_actions_simple.py \
#     --input-file tau_bench/sdg/synthetic_tasks_hard.json \
#     --output-file tau_bench/sdg/validated_tasks_hard.json

# echo "✅ Hard task validation completed!"
# echo ""

# # Count validated sequences for summary
# echo "📊 Counting validated sequences..."
# EASY_COUNT=$(python -c "import json; print(len(json.load(open('tau_bench/sdg/validated_tasks_easy.json'))))" 2>/dev/null || echo "0")
# MEDIUM_COUNT=$(python -c "import json; print(len(json.load(open('tau_bench/sdg/validated_tasks_medium.json'))))" 2>/dev/null || echo "0")
# HARD_COUNT=$(python -c "import json; print(len(json.load(open('tau_bench/sdg/validated_tasks_hard.json'))))" 2>/dev/null || echo "0")
# TOTAL_VALIDATED=$((EASY_COUNT + MEDIUM_COUNT + HARD_COUNT))

# # Summary
# echo "🎉 Synthetic data generation and validation complete!"
# echo ""
# echo "Generated files:"
# echo "  📁 tau_bench/sdg/synthetic_tasks_easy.json      (30 easy tasks - raw)"
# echo "  📁 tau_bench/sdg/synthetic_tasks_medium.json    (30 medium tasks - raw)"
# echo "  📁 tau_bench/sdg/synthetic_tasks_hard.json      (30 hard tasks - raw)"
# echo ""
# echo "Validated files:"
# echo "  📁 tau_bench/sdg/validated_tasks_easy.json      ($EASY_COUNT validated easy tasks)"
# echo "  📁 tau_bench/sdg/validated_tasks_medium.json    ($MEDIUM_COUNT validated medium tasks)"
# echo "  📁 tau_bench/sdg/validated_tasks_hard.json      ($HARD_COUNT validated hard tasks)"
# echo ""
# echo "📈 Validation Summary:"
# echo "  Total generated: 90 tasks (30 easy + 30 medium + 30 hard)"
# echo "  Total validated: $TOTAL_VALIDATED tasks"
# echo "  Success rate: $(python -c "print(f'{$TOTAL_VALIDATED/90*100:.1f}%')" 2>/dev/null || echo "N/A")"
# echo ""
# echo "✅ Validated sequences are ready for instruction generation and tau-bench formatting!"