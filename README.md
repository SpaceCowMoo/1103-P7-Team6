# 1103-P7-Team6

# INTERNLINK

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/SpaceCowMoo/1103-P7-Team6.git
cd 1103-P7-Team6
```

2. **Set up the Environment Variables:**

Windows (PowerShell):
```bash
Copy-Item .env.example .env
```

macOS / Linux / Git Bash:
```bash
cp .env.example .env
```

3. **Build the Docker image:**

```bash
docker build -t internlink .
```

4. **Run the Application:**

Windows (PowerShell):
```bash
docker run --rm -it -v "${PWD}/data:/app/internlink/data" internlink
```

macOS / Linux / Git Bash:
```bash
docker run --rm -it -v "$(pwd)/data:/app/internlink/data" internlink
```