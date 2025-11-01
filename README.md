# Valid Social CLI 📱

A powerful command-line tool designed to automate posting to multiple social media platforms, including Instagram and X (formerly Twitter), directly from your terminal.

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Version](https://img.shields.io/badge/version-0.1.0-green)

---

## Overview

Valid Social streamlines your social media workflow by leveraging browser automation to post content on your behalf. It uses a persistent browser profile to save your login sessions, so you only need to log in once. The interactive CLI guides you through selecting platforms, writing captions, and uploading media, making cross-platform posting fast and efficient.

## ✨ Features

-   **Multi-Platform Support**: Post to Instagram and X simultaneously. Support for Facebook and TikTok is planned for future releases.
-   **Persistent Login**: Log in once manually through the CLI. Your session is securely saved for all future automated posts.
-   **Interactive Interface**: An intuitive command-line interface guides you through composing your posts, from writing captions to selecting media.
-   **Media Uploads**: Attach images and videos to your posts with a simple file selector.
-   **Stealth Automation**: Utilizes Playwright with stealth configurations to mimic human behavior and reduce the risk of detection.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

-   Python 3.9+
-   `pip` and `venv`

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/thevalidcode/valid-social.git
    cd valid-social
    ```

2.  **Create and Activate a Virtual Environment**
    -   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies**
    Install the project and its dependencies from `pyproject.toml`.
    ```bash
    pip install .
    ```

4.  **Install Browser Binaries**
    Playwright requires browser binaries to function. This command will download them.
    ```bash
    playwright install
    ```

## ⚙️ Usage

Using Valid Social involves two main steps: logging in to save your session and then creating posts.

### 1. Login to a Platform

You must first log in to each platform you want to automate. This command opens a browser window for you to log in manually. Once you're done, your session cookies are saved for future use.

-   **For Instagram:**
    ```bash
    valid-social login --platform instagram
    ```

-   **For X (Twitter):**
    ```bash
    valid-social login --platform x
    ```

After running the command, a browser will open. Log in to your account as you normally would. Once you see your feed, you can close the browser and return to the terminal.

### 2. Create a Post

To create a new post, use the `post` command. You can run it interactively or provide all the details via flags.

#### Interactive Mode

This is the easiest way to get started. The CLI will prompt you for each step.

```bash
valid-social post
```

You will be guided through:
1.  **Selecting Platforms**: A numbered list of available platforms will be displayed.
2.  **Writing a Caption**: An editor will open for you to type your caption. Type `END` on a new line to finish.
3.  **Uploading Media**: A system file picker will open, allowing you to select one or more images/videos.

#### Non-Interactive Mode (with flags)

You can also provide all the information directly as command-line arguments. This is useful for scripting.

```bash
valid-social post --platform Instagram --platform X --caption "Check out this amazing photo! #automation #python" --media "/path/to/your/image.jpg"
```

## 🛠️ Technologies Used

| Technology                                               | Description                                        |
| -------------------------------------------------------- | -------------------------------------------------- |
| [Python](https://www.python.org/)                        | The core programming language used for the project. |
| [Typer](https://typer.tiangolo.com/)                     | A modern and intuitive library for building CLIs.  |
| [Playwright](https://playwright.dev/python/)             | A powerful library for reliable browser automation. |

## 🤝 Contributing

Contributions are welcome! If you have an idea for a new feature or have found a bug, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch**: `git checkout -b feature/your-feature-name`
3.  **Make your changes** and commit them: `git commit -m 'Add some feature'`
4.  **Push to the branch**: `git push origin feature/your-feature-name`
5.  **Open a Pull Request** and describe your changes.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Ibeh Precious (Valid)**

-   **Email**: `thevalidcode@gmail.com`
-   **Twitter**: [@your-twitter-handle](https://twitter.com/your-twitter-handle)
-   **LinkedIn**: [your-linkedin-profile](https://www.linkedin.com/in/your-linkedin-profile/)

---

[![Readme was generated by Dokugen](https://img.shields.io/badge/Readme%20was%20generated%20by-Dokugen-brightgreen)](https://www.npmjs.com/package/dokugen)