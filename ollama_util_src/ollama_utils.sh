#!/bin/bash

# 列出所有模型
ollama list

# 修改模型ctx
touch ModelFile
nano ModelFile
# From deepseek-r1:32b-qwen-distill-q4_K_M
# PARAMETER num_ctx 1048576
# 修改模型ctx
ollama create -f ModelFile deepseek-r1:32b-qwen-distill-ctx_1048576-q4_K_M
