# Python Fullstack Challenge

## Introduction

Hi! You applied for a position in one of our development teams and you impressed us in the first interview. Now we would like to see you in action. A part of the recruiting process consists of a coding challenge involving this repository, which contains a very simple, fake chatbot.

## Your task

This application allows you to talk to a chatbot called Bob. Unfortunately, there is only a single message history, so it is hard to keep track of different topics. To solve this, we want to allow the user to start multiple conversations.

Requirements:

- The user can easily start a new, empty conversation.
- The user can switch between existing conversations, for example with a sidebar or dropdown.
- Bonus: The final design also works well on small screens, e.g. smartphones.

Out of scope:

- There is no need for advanced management features, like naming, ordering or deleting them.
- Conversations don't need to be persisted. You can keep them in memory only.

If you are unsure about further requirements, feel free to make assumptions and document them or tell us about them in the interview. There is no single 100% correct solution to this challenge.

## Submitting your results

To submit your results, please do the following:

1. Locally commit your changes in one or multiple commits using git.
2. Zip the whole folder and mail it back to the person who originally sent you this challenge.

There is no need to provide any additional documentation - we will talk about your solution in the next interview.

## The interview

In the tech interview, we would like you to present your solution: First from a user perspective, then with more technical details. We will talk about it, probably ask some questions and then make some more, small changes - so please be prepared to screen-share your development environment with us. Also: Don't panic! We promise, we're nice.

## Running the application

We recommend to use at least **Python 3.12** and **Node.js 22** to run this application.

To start the backend, navigate to the `backend` directory, install the required packages and start the dev server. We recommend to use some kind of virtual environment, e.g. by running `python -m venv .venv` or using your IDE.

Example:

```sh
cd backend
pip install -r requirements.txt
fastapi dev main.py
```

To start the frontend, navigate to the `frontend` directory, install the required packages and start the dev server.

Example:

```sh
cd frontend
npm ci
npm run dev
```
