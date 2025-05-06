# Requirements
pip3 install -U langchain langchain-openai langchain-community openai

# Ensure you have make or GCC
git clone https://github.com/devshane/zork.git
cd zork && make

# Run as Human
./zork

cd ..
chmod +x ./zork




git clone https://github.com/openai/openai-agents-python.git
cd openai-agents-python
pip install -e .
pip install requests python-dotenv pydantic
