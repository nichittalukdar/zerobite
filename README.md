# ZeroBite frontend

Clean connected prototype structure:

frontend1/
├── index.html
├── css/
│   ├── style.css
│   ├── auth.css
│   └── admin.css
├── js/
│   ├── script.js
│   ├── auth.js
│   ├── donor.js
│   ├── receiver.js
│   └── admin.js
└── pages/
    ├── donor.html
    ├── receiver.html
    ├── admin.html
    ├── login.html
    └── signup.html

Run with Live Server from the frontend1 folder.

Prototype storage:
- zeroBiteUsers
- zeroBiteCurrentUser
- shareBiteFoods

Prototype admin:
- email: admin@zerobite.local
- password: admin123

For production, replace localStorage authentication with a real backend and hashed passwords.
