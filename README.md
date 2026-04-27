# AI-object-tech


curl http://localhost:8078/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {"role": "user", "content": "Привет! Ты работаешь?"}
  ]
}'

docker model run hf.co/unsloth/gemma-4-E4B-it-GGUF:UD-Q6_K_XL