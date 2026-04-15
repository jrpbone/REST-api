// Client 1 - Node.js terminal client
const DEFAULT_BASES = [
    'http://localhost/REST/REST%20API/my-api/api/index.php',
    'http://localhost:8080/REST/REST%20API/my-api/api/index.php',
    'https://localhost:4433/REST/REST%20API/my-api/api/index.php'
];

const BASES = (process.env.API_BASE || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);

const API_BASES = BASES.length > 0 ? BASES : DEFAULT_BASES;

function buildRouteUrls(path) {
    const route = path.replace(/^\/+/, '');
    return API_BASES.map((base) => `${base}?route=${encodeURIComponent(route)}`);
}

async function request(method, path, body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    const urls = buildRouteUrls(path);
    const errors = [];

    for (const url of urls) {
        try {
            const res = await fetch(url, options);
            const text = await res.text();
            const data = JSON.parse(text);
            console.log(`[${method} ${path}] (${res.status}) via ${url}`, data);
            return data;
        } catch (err) {
            errors.push(`${url} -> ${err.message}`);
        }
    }

    console.error(`[ERROR] Request failed after trying all configured API URLs.`);
    errors.forEach((entry) => console.error(`  ${entry}`));
}

async function main() {
    console.log("=== REST API Client Demo ===\n");
    console.log("API fallback order:");
    API_BASES.forEach((base) => console.log(`- ${base}`));
    console.log('');

    // REGISTER
    console.log("-- Register --");
    await request('POST', '/register', { username: "tech-it-easy", password: "1234" });
    await request('POST', '/register', { username: "tech-it-easy", password: "1234" });
    await request('POST', '/register', { username: "ab", password: "1234" });

    // LOGIN
    console.log("\n-- Login --");
    await request('POST', '/login', { username: "tech-it-easy", password: "1234" });
    await request('POST', '/login', { username: "tech-it-easy", password: "wrong" });
    await request('POST', '/login', { username: "ghost", password: "1234" });

    // READ
    console.log("\n-- Read Users --");
    await request('GET', '/users');
    await request('GET', '/users/tech-it-easy');
    await request('GET', '/users/nobody');

    // UPDATE
    console.log("\n-- Update Password --");
    await request('PUT', '/users/tech-it-easy', { password: "newpass99" });
    await request('POST', '/login', { username: "tech-it-easy", password: "newpass99" });

    // DELETE
    console.log("\n-- Delete User --");
    await request('DELETE', '/users/tech-it-easy');
    await request('GET', '/users');
}

main();