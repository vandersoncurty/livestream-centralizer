const express = require("express");
const session = require("express-session");
const bodyParser = require("body-parser");
const fetch = require("node-fetch");

const app = express();
const PORT = 3000;

// Configuração de middleware
app.set("view engine", "ejs");
app.use(express.static("public"));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({ secret: "streamSecret", resave: false, saveUninitialized: false }));

// Simula um banco de usuários
const users = { admin: "password123" };

// Rota de login
app.get("/", (req, res) => {
  res.render("login", { error: null });
});

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (users[username] && users[username] === password) {
    req.session.user = username;
    res.redirect("/dashboard");
  } else {
    res.render("login", { error: "Credenciais inválidas!" });
  }
});

// Middleware de autenticação
const isAuthenticated = (req, res, next) => {
  if (req.session.user) return next();
  res.redirect("/");
};

// Dashboard
app.get("/dashboard", isAuthenticated, async (req, res) => {
  const response = await fetch("http://backend:5000/destinations");
  const destinations = await response.json();
  res.render("dashboard", { destinations });
});

// Atualizar destinos
app.post("/update", isAuthenticated, async (req, res) => {
  const { type, server, key } = req.body;
  await fetch("http://backend:5000/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      type,
      destinations: [{ server, key }],
    }),
  });
  res.redirect("/dashboard");
});

app.listen(PORT, () => {
  console.log(`Frontend running on http://localhost:${PORT}`);
});
