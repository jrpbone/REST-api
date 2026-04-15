# Group REST API Enhancement and Multi-Client Implementation

## Overview

This repository contains a small user management project built for the REST API activity.

The repository includes:
- a PHP backend served through XAMPP
- a browser client
- a Node.js terminal client
- a Python Tkinter desktop client

The main application folder is `my-api/`.

## Repository Structure

```text
REST API/
|-- my-api/
|   |-- api/
|   |   |-- index.php
|   |   `-- users.json
|   |-- client.js
|   |-- index.html
|   |-- tkinter_client.py
|   |-- package.json
|   `-- package-lock.json
|-- Activity Group REST API.pdf
|-- API_DOCUMENTATION.md
|-- JOURNAL_TEMPLATE.md
`-- README.md
```

## Requirements

Install or prepare the following:
- XAMPP with Apache
- Node.js
- Python 3

## Project Location

Place the repository in:

```text
C:\xampp\htdocs\REST\REST API
```

## How to Run the Repository

### 1. Start the backend

1. Open XAMPP Control Panel.
2. Start `Apache`.
3. Make sure the repository is inside `C:\xampp\htdocs\REST\REST API`.

### 2. Supported local ports

The clients are configured to try common local Apache URLs automatically.

Fallback order includes:
- `http://localhost/...` on port `80`
- `http://localhost:8080/...`
- `https://localhost:4433/...`

This allows the project to still run even if your XAMPP setup does not use the default web ports.

### 3. Open the browser client

Open this URL in your browser:

```text
http://localhost/REST/REST%20API/my-api/index.html
```

If your Apache setup is not using port `80`, the browser client will still try the fallback API URLs internally.

### 4. Run the Node.js client

Open a terminal and run:

```powershell
cd C:\xampp\htdocs\REST\REST API\my-api
npm run client
```

The Node client will automatically try the supported local API URLs in sequence.

### 5. Run the Python Tkinter client

Open a terminal and run:

```powershell
cd C:\xampp\htdocs\REST\REST API\my-api
python tkinter_client.py
```

The Tkinter client also supports automatic fallback across the configured local ports.

## Files You Will Use Most

- `my-api/api/index.php`
  Main backend file.
- `my-api/index.html`
  Browser-based client.
- `my-api/client.js`
  Node.js terminal client.
- `my-api/tkinter_client.py`
  Python desktop client.

## Notes

- Start Apache before using any client.
- The browser client is the quickest way to test the project manually.
- The Node.js and Tkinter clients consume the same backend.
- Detailed endpoint and API behavior are documented in `API_DOCUMENTATION.md`.