conda create --name llm_p python=3.12 -y
conda activate llm_p

pip install openai

python ./src/crew.py