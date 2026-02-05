#!/bin/bash
# 基线服务启动脚本 (对照组)
# 端口: 10001, NPU: 12,13

export ASCEND_RT_VISIBLE_DEVICES=12,13

vllm serve /data2/weights/Qwen_Qwen3-32B \
     -tp 2 \
     --port 10001 \
     --served-model-name Qwen3-32B \
     --speculative-config '{    
     "model": "/data2/weights/scd/RedHatAI/Qwen3-32B-speculator.eagle3",
     "num_speculative_tokens": 4,
     "method": "eagle3",
     "draft_tensor_parallel_size": 1,
     "enable_adaptive": false
   }' \
     --additional-config '{"ascend_compilation_config":{"decode_gear_list":[24]}}' \
     --max-num-seqs 16
