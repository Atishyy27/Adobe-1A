# Adobe Hackathon - Round 1A: PDF Outline Extractor

This project is a solution for Round 1A of the Adobe "Connecting the Dots" Hackathon.

## Description

The goal of this project is to create a command-line tool that runs inside a Docker container. It processes PDF files from an input directory, extracts a structured outline (Title, H1, H2, H3), and outputs the result as a JSON file.

### How to Build
```bash
docker build --platform linux/amd64 -t adobe-1a-solution .
```

### How to Run
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none adobe-1a-solution
```