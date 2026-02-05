#!/bin/bash
# 自适应服务启动脚本 (实验组)
# 端口: 10000, NPU: 14,15

export ASCEND_RT_VISIBLE_DEVICES=14,15

vllm serve /data2/weights/Qwen_Qwen3-32B \
     -tp 2 \
     --port 10000 \
     --served-model-name Qwen3-32B \
     --speculative-config '{    
     "model": "/data2/weights/scd/RedHatAI/Qwen3-32B-speculator.eagle3",
     "num_speculative_tokens": 4,
     "method": "eagle3",
     "draft_tensor_parallel_size": 1,
     "enable_adaptive": true
   }' \
     --additional-config '{"ascend_compilation_config":{"decode_gear_list":[24]}}' \
     --max-num-seqs 16
