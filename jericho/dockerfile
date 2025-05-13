FROM python:3.10-slim
WORKDIR /app

# Install deps
RUN apt-get update && apt-get install -y \
    wget unzip gcc g++ build-essential cmake && apt-get clean

# Download and unpack games
RUN wget -q https://github.com/BYU-PCCL/z-machine-games/archive/master.zip \
 && unzip -q master.zip \
 && mkdir -p /app/games \
 && mv z-machine-games-master/jericho-game-suite /app/games/jericho-game-suite \
 && mv z-machine-games-master/autoplay-game-suite /app/games/autoplay-game-suite \
 && rm -rf master.zip z-machine-games-master

# Copy app code
COPY main.py /app/main.py
COPY api /app/api
COPY requirements.txt /app/requirements.txt

# Install Python deps + spaCy model
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m spacy download en_core_web_sm

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
