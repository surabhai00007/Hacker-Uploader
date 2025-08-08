FROM python:3.10-alpine

# Working directory set
WORKDIR /app

# Copy dependency list first for better caching
COPY requirements.txt .

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    libffi-dev \
    musl-dev \
    ffmpeg \
    aria2 \
    make \
    g++ \
    cmake \
    unzip \
    wget \
    tar \
    bash \
    curl \
    zip \
    p7zip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Build and install mp4decrypt from Bento4
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip && \
    unzip v1.6.0-639.zip && \
    cd Bento4-1.6.0-639 && \
    mkdir build && cd build && \
    cmake .. && make -j$(nproc) && \
    cp mp4decrypt /usr/local/bin/ && \
    cd ../.. && rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# Default command to start the bot
CMD ["python3", "main.py"]