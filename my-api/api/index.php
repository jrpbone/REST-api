<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Simple file-based "database"
$dbFile = __DIR__ . '/users.json';

function loadUsers($dbFile) {
    if (!file_exists($dbFile)) return [];
    return json_decode(file_get_contents($dbFile), true) ?? [];
}

function saveUsers($dbFile, $users) {
    file_put_contents($dbFile, json_encode(array_values($users), JSON_PRETTY_PRINT));
}

function respond($status, $code, $data) {
    http_response_code($code);
    echo json_encode(array_merge(["status" => $status], $data));
    exit();
}

$users  = loadUsers($dbFile);
$method = $_SERVER['REQUEST_METHOD'];
$queryRoute = trim($_GET['route'] ?? '', '/');
$requestPath = trim(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH), '/');
$scriptName = trim($_SERVER['SCRIPT_NAME'] ?? '', '/');
$pathInfo = trim($_SERVER['PATH_INFO'] ?? '', '/');

if ($queryRoute !== '') {
    $path = $queryRoute;
} elseif ($pathInfo !== '') {
    $path = $pathInfo;
} else {
    // Fall back to trimming the actual script path so this works from nested XAMPP folders.
    $normalizedRequest = trim($requestPath, '/');
    $normalizedScript = trim($scriptName, '/');
    if ($normalizedScript !== '' && str_starts_with($normalizedRequest, $normalizedScript)) {
        $path = trim(substr($normalizedRequest, strlen($normalizedScript)), '/');
    } else {
        $path = '';
    }
}

$parts  = $path ? explode('/', $path) : [];
$body   = json_decode(file_get_contents("php://input"), true) ?? [];

// Route: POST /register
if ($method === 'POST' && isset($parts[0]) && $parts[0] === 'register') {
    $username = trim($body['username'] ?? '');
    $password = trim($body['password'] ?? '');

    if (!$username || !$password)
        respond("error", 400, ["message" => "Missing username or password"]);

    if (strlen($username) < 3)
        respond("error", 400, ["message" => "Username must be at least 3 characters"]);

    if (strlen($password) < 4)
        respond("error", 400, ["message" => "Password must be at least 4 characters"]);

    foreach ($users as $u) {
        if ($u['username'] === $username)
            respond("error", 409, ["message" => "Username already taken"]);
    }

    $users[] = ["username" => $username, "password" => $password];
    saveUsers($dbFile, $users);
    respond("success", 201, ["message" => "User '$username' registered successfully"]);
}

// Route: POST /login
if ($method === 'POST' && isset($parts[0]) && $parts[0] === 'login') {
    $username = trim($body['username'] ?? '');
    $password = trim($body['password'] ?? '');

    if (!$username || !$password)
        respond("error", 400, ["message" => "Missing username or password"]);

    $found = null;
    foreach ($users as $u) {
        if ($u['username'] === $username) { $found = $u; break; }
    }

    if (!$found)
        respond("error", 404, ["message" => "User not found"]);

    if ($found['password'] !== $password)
        respond("error", 401, ["message" => "Incorrect password"]);

    respond("success", 200, ["message" => "Welcome back, $username!"]);
}

// Route: GET /users
if ($method === 'GET' && isset($parts[0]) && $parts[0] === 'users' && !isset($parts[1])) {
    $safe = array_map(fn($u) => ["username" => $u['username']], $users);
    respond("success", 200, ["count" => count($safe), "users" => $safe]);
}

// Route: GET /users/{username}
if ($method === 'GET' && isset($parts[0]) && $parts[0] === 'users' && isset($parts[1])) {
    $username = $parts[1];
    foreach ($users as $u) {
        if ($u['username'] === $username)
            respond("success", 200, ["user" => ["username" => $u['username']]]);
    }
    respond("error", 404, ["message" => "User not found"]);
}

// Route: PUT /users/{username}
if ($method === 'PUT' && isset($parts[0]) && $parts[0] === 'users' && isset($parts[1])) {
    $username = $parts[1];
    $password = trim($body['password'] ?? '');

    if (!$password || strlen($password) < 4)
        respond("error", 400, ["message" => "New password must be at least 4 characters"]);

    foreach ($users as &$u) {
        if ($u['username'] === $username) {
            $u['password'] = $password;
            saveUsers($dbFile, $users);
            respond("success", 200, ["message" => "Password updated for '$username'"]);
        }
    }
    respond("error", 404, ["message" => "User not found"]);
}

// Route: DELETE /users/{username}
if ($method === 'DELETE' && isset($parts[0]) && $parts[0] === 'users' && isset($parts[1])) {
    $username = $parts[1];
    $newUsers = array_filter($users, fn($u) => $u['username'] !== $username);

    if (count($newUsers) === count($users))
        respond("error", 404, ["message" => "User not found"]);

    saveUsers($dbFile, $newUsers);
    respond("success", 200, ["message" => "User '$username' deleted"]);
}

respond("error", 404, ["message" => "Route not found"]);