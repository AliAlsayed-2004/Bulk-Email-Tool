# Lution Email Purchasing Tool 📧

Welcome to the **Lution Email Purchasing Tool**! 🚀 This Python script automates bulk purchasing of email accounts (HOTMAIL and OUTLOOK) via the Lution API. With a colorful CLI interface, multi-threading, and secure API key handling, it’s designed for efficiency and ease of use. 📊

## Table of Contents 📑
- [Features](#features-✨)
- [Prerequisites](#prerequisites-🛠️)
- [Installation](#installation-⚙️)
- [Configuration](#configuration-🔧)
- [Usage](#usage-🚀)
  - [Interactive Mode](#interactive-mode-🖥️)
  - [CLI Mode](#cli-mode-⌨️)
- [File Structure](#file-structure-📂)
- [Error Handling](#error-handling-🛡️)
- [Contributing](#contributing-🤝)
- [License](#license-📜)
- [Contact](#contact-📬)

## Features ✨
- 🛒 **Bulk Email Purchasing**: Purchase HOTMAIL or OUTLOOK email accounts in bulk via the Lution API.
- 🧵 **Multi-Threading**: Configurable threads (up to 20) for faster processing.
- 🔒 **Secure API Key Storage**: Encrypts API keys and supports environment variables.
- 🎨 **Colorful CLI**: Enhanced with `colorama` and `pyfiglet` for an engaging terminal experience.
- 📈 **Real-Time Stats**: Tracks purchased emails, attempts, success rate, and elapsed time.
- 📝 **Error Logging**: Detailed error logs for easy debugging.
- 🔄 **Retry Mechanism**: Handles rate limits and connection errors with automatic retries.
- 📄 **Output Management**: Saves purchased email credentials to a specified file.

## Prerequisites 🛠️
To use this tool, you need:
- 🐍 **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- 🌐 **Lution API Key**: Obtain from [Lution](https://lution.ee)
- 📦 **Required Python Packages**: Listed in `requirements.txt`

## Installation ⚙️
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/lution-email-tool.git
   cd lution-email-tool
   ```

2. **Install Dependencies**:
   Create a virtual environment (recommended) and install packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Required packages:
   - `requests`
   - `colorama`
   - `pyfiglet`
   - `argparse`
   - `urllib3`

## Configuration 🔧
1. **Create Configuration File**:
   The script uses a `config.json` file in the `config/` directory. A default configuration is created if none exists:
   ```json
   {
       "API_BASE_URL": "https://api.lution.ee",
       "TIMEOUT": 10,
       "REQUEST_DELAY": 0.5,
       "MAX_THREADS": 20
   }
   ```
   Modify `config/config.json` to adjust settings like `API_BASE_URL` or `MAX_THREADS`.

2. **API Key Setup**:
   Set the `LUTION_API_KEY` environment variable:
   ```bash
   export LUTION_API_KEY="your-api-key"  # On Windows: set LUTION_API_KEY=your-api-key
   ```
   Alternatively, the script prompts for the API key at runtime and can save it encrypted in `config.enc`.

3. **Optional Proxies**:
   Add proxy servers to `proxies.txt` (one per line):
   ```
   http://proxy1:port
   http://proxy2:port
   ```

## Usage 🚀
The tool supports two modes: Interactive and CLI.

### Interactive Mode 🖥️
Run without arguments to enter the interactive menu:
```bash
python lution_email_tool.py
```
- Displays a colorful ASCII banner.
- Choose options to buy emails, view stats, or exit.
- For purchasing:
  - Select mail type (`HOTMAIL` or `OUTLOOK`).
  - Specify quantity, thread count, and output file.

### CLI Mode ⌨️
Run with arguments for automated execution:
```bash
python lution_email_tool.py --cli --mail HOTMAIL --quantity 100 --threads 10 --output accounts.txt
```
- `--cli`: Enables CLI mode.
- `--mail`: Specify `HOTMAIL` or `OUTLOOK`.
- `--quantity`: Number of emails to purchase.
- `--threads`: Number of threads (1–20, default: 5).
- `--output`: Output file for credentials (default: `accounts.txt`).

**Example**:
```bash
python lution_email_tool.py --cli --mail OUTLOOK --quantity 50 --threads 5 --output outlook_accounts.txt
```

## File Structure 📂
```
lution-email-tool/
├── config/
│   ├── config.json       # Configuration file
│   ├── config.enc        # Encrypted API key (optional)
├── logs/
│   ├── errors.log        # Error logs
│   ├── session_stats.log # Session statistics
├── proxies.txt           # Optional proxy list
├── accounts.txt          # Default output for purchased emails
├── lution_email_tool.py  # Main script
├── README.md             # This file
└── requirements.txt      # Dependencies
```

## Error Handling 🛡️
- **Logs**: Errors are saved to `logs/errors.log` with timestamps.
- **Retries**: Failed API requests are retried automatically.
- **Rate Limits**: Handles HTTP 429 errors by pausing and retrying.
- **Configuration Errors**: Exits gracefully if `config.json` is missing or invalid.

## Contributing 🤝
Contributions are welcome! 🙌 Follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request.

Report issues or suggest features on the [GitHub Issues page](https://github.com/yourusername/lution-email-tool/issues).

## License 📜
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact 📬
For questions or support, reach out via:
- 📧 **Email**: your.email@example.com
- 🌐 **GitHub**: [yourusername](https://github.com/yourusername)
- 🐦 **X**: [@yourhandle](https://x.com/yourhandle)

Happy email purchasing! 🎉