# Project OSUS - Open Source URL Shortener 🎉

Welcome to **Project OSUS**, an open-source URL shortener initiative built with **Flask**, **Python**, and **MongoDB**! This project is part of **Hacktoberfest 2024**, and we're inviting contributions from everyone, whether you're a techie or not.

The goal of this project is to create a simple and efficient URL shortener while fostering learning and collaboration. Contributions can be technical (code) or non-technical (documentation, design), and we encourage everyone to get involved!

---

## Table of Contents
- [What is HacktoberFest](#hacktober-fest)
- [About the Project](#about-the-project)
- [Tech Stack](#tech-stack)
- [Live Demo](#live-demo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Project](#running-the-project)
- [Contributing](#contributing)
  - [How to Contribute](#how-to-contribute)
  - [Tech Contributions](#tech-contributions)
  - [Non-Tech Contributions](#non-tech-contributions)
- [License](#license)
- [Contact](#contact)


## What is HacktoberFest

**Hacktoberfest** is an annual event celebrated in October, organized by DigitalOcean, GitHub, and other partners, to encourage open-source contributions. During this month, developers of all skill levels are invited to contribute to open-source projects, celebrate their achievements, and connect with the community.

You get to enhance your coding and collaboration skills, connect with like-minded developers and industry professionals and get some recognition and prizes too :)

**Important Note:** Make sure you've registered in [Hacktoberfest website](https://hacktoberfest.com/) with your Github account. This will track your contributions for the event and ensure you receive your rewards.

---

## About the Project
**Project OSUS** is a URL Shortener that allows users to generate shortened URLs that redirect to longer URLs. The project is built with Flask (Python) on the backend and MongoDB for data storage.

Whether you’re a developer, writer, designer, or tester, there are various ways to contribute and learn through this open-source project.

### How it Works:
1. **Long URL**: The user inputs a long URL, for example:  
   `https://www.reddit.com/r/ProgrammerHumor/comments/m7xi4j/should_i_contribute_or_work_on_kaggle/`
   
2. **Short URL**: The system generates a short URL, for example:  
   `https://project-osus.vercel.app/meme` [click here](https://project-osus.vercel.app/meme)

When users visit the short URL, they are automatically redirected to the original long URL. This makes it easy to share and manage links efficiently.

---

## Tech Stack
- **Backend:** Flask (Python)
- **Database:** MongoDB
- **Frontend:** HTML, CSS, JS (with flexibility to improve)
- **Version Control:** Git/GitHub

---

## Live Demo

🚀 All the changes you contribute will go live on our official website:  
**https://project-osus.vercel.app/**

This means that every improvement you make, whether it's fixing bugs, adding features, or refining the user interface, will be reflected in the live application for everyone to use. 

Your contributions will help make **Project OSUS** better for the community, and you'll get the satisfaction of seeing your work in action!

Ready to make an impact? Start contributing today and watch your work go live! 🌟

---

## Getting Started

Here’s how to get the project running on your local machine.

### Prerequisites
Make sure you have the following installed on your system:
- **Python**
- **MongoDB** (Local installation or Cloud version)
- **Git** (for version control)

### Installation

1. **Fork the Repository**: First, fork the repository to create a personal copy in your GitHub account.

2. **Clone the Repository**: Clone your forked repository to your local machine using the command:

   ```bash
   git clone https://github.com/your-username/repo-name.git
    ```

2. **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate  # Windows
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    
4. **Create a `.env` file**: In the root directory of your project, create a file named `.env` and add the following environment variables to the file:
    
    ```plaintext
   MONGO_PATH='localhost'
   MONGO_PORT=27017

**Note:** If you are using a cloud version of MongoDB, make sure to change MONGO_PATH to your cloud connection string. The connection string format typically looks like this: mongodb+srv://myUser:myPassword@ cluster0.mongodb.net/

### Running the Project

1. **Start MongoDB** (if running locally):
    ```bash
    mongod
    ```

2. **Run the Flask development server**:
    ```bash
    flask run
    ```

3. The project will be running at `http://localhost:5000`. Visit that in your browser to start using the URL shortener!

---

## Contributing

We encourage contributions from everyone! Whether you're looking to contribute code, documentation, design, or testing, here's how you can get involved.

### How to Contribute

1. **Fork the repository**:
   - Go to the main repository page and click on the "Fork" button in the top right corner.

2. **Raise an issue**:
   - Before starting to work on a new feature or bug fix, check if there’s an existing issue related to it. If not, [open a new issue](https://github.com/harshithtunuguntla/project-osus/issues).
   - If you're working on an existing issue, leave a comment on that issue thread saying you're working on it to avoid duplicating efforts.

3. **Create a new branch**:
   - Create a branch for your contribution. Use a descriptive name for your branch, such as `fix-issue-#number` or `add-new-feature`:
     ```bash
     git checkout -b branch-name
     ```

4. **Make your changes**:
   - Make sure your code follows the project structure and **use autopep8 for code formatting** to ensure consistency:


5. **Commit your changes**:
   - Write a meaningful commit message describing your changes:
     ```bash
     git add .
     git commit -m "Description of your changes"
     ```

6. **Push to your forked repository**:
   ```bash
   git push origin branch-name

7. **Create a pull request (PR)**:

    Once your changes are pushed, come back to this repository on GitHub. You should see a prompt to create a pull request (PR). Click on it and fill in the details about your changes, explaining why you made them.
    
 **And that's it! You have successfully made your contribution. The maintainers will review your PR and provide feedback or merge it if everything looks good.** 

---

### Tech Contributions

- **Bug Fixes**: Find and fix bugs to improve the project.
- **Feature Enhancements**: Add new features, such as custom URLs, user authentication, or analytics.
- **Code Quality**: Refactor and improve code quality or performance.
- **UI/UX**: Help improve the front-end design or overall user experience.

---

### Non-Tech Contributions

- **Documentation**: Improve this README or create new guides for contributors.
- **Testing**: Write test cases or help test the project for bugs.
- **Design**: Create graphics, logos, or improve the UI design.

---

### License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

---

### Contact

Got questions, or need help or you want to help maintainers?? Feel free to reach out via issues or via:

<a href="https://chat.whatsapp.com/GGFHTgViPUgIbV2EB9Ymm7"><img alt="Whatsapp" src="https://img.shields.io/badge/Whatsapp-25d366?style=for-the-badge&logo=whatsapp&logoColor=white">  <a  href="https://instagram.com/harshith.presents"><img alt="Instagram" src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white">
