import json
import os
import ssl
import threading
import urllib.error
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

DEFAULT_BASES = [
    "http://localhost/REST/REST%20API/my-api/api/index.php",
    "http://localhost:8080/REST/REST%20API/my-api/api/index.php",
    "https://localhost:4433/REST/REST%20API/my-api/api/index.php",
]


def parse_base_urls():
    raw_value = os.environ.get("API_BASE", "")
    custom_values = [value.strip() for value in raw_value.split(",") if value.strip()]
    return custom_values if custom_values else DEFAULT_BASES.copy()


class TkinterApiClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("User Management Desktop Client")
        self.geometry("980x700")
        self.minsize(900, 640)

        self.base_urls = parse_base_urls()
        self.api_var = tk.StringVar(value="Fallback API targets: " + ", ".join(self.base_urls))
        self.status_var = tk.StringVar(value="Ready")
        self._busy = False
        self._action_buttons = []
        self._build_layout()

    def _build_layout(self):
        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="User Management Desktop Client",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            textvariable=self.api_var,
            foreground="#555555",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(header, textvariable=self.status_var).grid(row=0, column=1, rowspan=2, sticky="e")

        body = ttk.Panedwindow(container, orient="vertical")
        body.grid(row=1, column=0, sticky="nsew")

        client_frame = ttk.Frame(body, padding=8)
        client_frame.columnconfigure(0, weight=1)
        client_frame.rowconfigure(0, weight=1)
        body.add(client_frame, weight=3)

        response_frame = ttk.LabelFrame(body, text="Response Viewer", padding=8)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)
        body.add(response_frame, weight=2)

        notebook = ttk.Notebook(client_frame)
        notebook.grid(row=0, column=0, sticky="nsew")

        self._build_register_tab(notebook)
        self._build_login_tab(notebook)
        self._build_users_tab(notebook)
        self._build_update_tab(notebook)
        self._build_delete_tab(notebook)

        self.response_box = ScrolledText(response_frame, wrap="word", font=("Consolas", 10), height=16)
        self.response_box.grid(row=0, column=0, sticky="nsew")
        self.response_box.insert("1.0", "Responses will appear here.\n")
        self.response_box.configure(state="disabled")

    def _build_register_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text="Register")

        self.reg_username = self._add_entry(frame, 0, "Username")
        self.reg_password = self._add_entry(frame, 1, "Password", show="*")
        self._make_button(frame, "Register User", self.register_user).grid(row=2, column=0, sticky="w", pady=(12, 0))

    def _build_login_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text="Login")

        self.login_username = self._add_entry(frame, 0, "Username")
        self.login_password = self._add_entry(frame, 1, "Password", show="*")
        self._make_button(frame, "Login", self.login_user).grid(row=2, column=0, sticky="w", pady=(12, 0))

    def _build_users_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        notebook.add(frame, text="Users")

        button_row = ttk.Frame(frame)
        button_row.grid(row=0, column=0, sticky="w")
        self._make_button(button_row, "Get All Users", self.get_all_users).pack(side="left")

        lookup_row = ttk.Frame(frame)
        lookup_row.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        lookup_row.columnconfigure(1, weight=1)
        ttk.Label(lookup_row, text="Username").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.lookup_username = ttk.Entry(lookup_row)
        self.lookup_username.grid(row=0, column=1, sticky="ew")
        self._make_button(lookup_row, "Get User", self.get_one_user).grid(row=0, column=2, padx=(8, 0))

        self.users_table = ttk.Treeview(frame, columns=("username",), show="headings", height=12)
        self.users_table.heading("username", text="Username")
        self.users_table.column("username", anchor="w", width=240)
        self.users_table.grid(row=3, column=0, sticky="nsew", pady=(16, 0))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.users_table.yview)
        scrollbar.grid(row=3, column=1, sticky="ns", pady=(16, 0))
        self.users_table.configure(yscrollcommand=scrollbar.set)

    def _build_update_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text="Update")

        self.update_username = self._add_entry(frame, 0, "Username")
        self.update_password = self._add_entry(frame, 1, "New Password", show="*")
        self._make_button(frame, "Update Password", self.update_user).grid(row=2, column=0, sticky="w", pady=(12, 0))

    def _build_delete_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text="Delete")

        self.delete_username = self._add_entry(frame, 0, "Username")
        self._make_button(frame, "Delete User", self.delete_user).grid(row=1, column=0, sticky="w", pady=(12, 0))

    def _add_entry(self, frame, row, label, show=None):
        frame.columnconfigure(0, weight=1)
        ttk.Label(frame, text=label).grid(row=row * 2, column=0, sticky="w")
        entry = ttk.Entry(frame, show=show)
        entry.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(4, 0))
        return entry

    def _make_button(self, parent, text, command):
        button = ttk.Button(parent, text=text, command=command)
        self._action_buttons.append(button)
        return button

    def _set_busy(self, busy, message=None):
        self._busy = busy
        for button in self._action_buttons:
            button.configure(state="disabled" if busy else "normal")
        if message:
            self.status_var.set(message)

    def _route_url(self, base_url, route):
        encoded_route = urllib.parse.quote(route.lstrip("/"), safe="/")
        return f"{base_url}?route={encoded_route}"

    def _build_ssl_context(self, url):
        if url.startswith("https://localhost") or url.startswith("https://127.0.0.1"):
            return ssl._create_unverified_context()
        return None

    def _perform_request(self, method, route, payload=None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        errors = []

        for base_url in self.base_urls:
            url = self._route_url(base_url, route)
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method=method,
            )

            try:
                with urllib.request.urlopen(req, timeout=8, context=self._build_ssl_context(url)) as response:
                    status = response.getcode()
                    raw = response.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read().decode("utf-8", errors="replace")
            except urllib.error.URLError as exc:
                errors.append(f"{url} -> {exc.reason}")
                continue
            except Exception as exc:
                errors.append(f"{url} -> {exc}")
                continue

            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                errors.append(f"{url} -> non-JSON response")
                continue

            return method, route, status, parsed, url

        return method, route, 0, {
            "status": "error",
            "message": "Could not reach any configured API URL.",
            "tried": errors,
        }, None

    def _dispatch_request(self, method, route, payload=None, after_response=None):
        if self._busy:
            self._show_response("LOCAL", "busy", 0, {
                "status": "error",
                "message": "Please wait for the current request to finish.",
            }, None)
            return

        self._set_busy(True, f"{method} {route} -> working...")

        def worker():
            result = self._perform_request(method, route, payload)
            self.after(0, lambda: self._finish_request(result, after_response))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_request(self, result, after_response=None):
        method, route, status, payload, used_url = result
        self._show_response(method, route, status, payload, used_url)
        if after_response is not None:
            after_response(payload)
        if used_url:
            self.status_var.set(f"{method} {route} -> {status} via {used_url}")
        else:
            self.status_var.set(f"{method} {route} -> ERROR")
        self._set_busy(False)

    def _show_response(self, method, route, status, payload, used_url):
        pretty = json.dumps(payload, indent=2)
        prefix = f"{method} {route}\nStatus: {status}"
        if used_url:
            prefix += f"\nURL: {used_url}"
        self.response_box.configure(state="normal")
        self.response_box.delete("1.0", "end")
        self.response_box.insert("1.0", f"{prefix}\n\n{pretty}")
        self.response_box.configure(state="disabled")

    def _require_value(self, entry, field_name):
        value = entry.get().strip()
        if not value:
            self._show_response("LOCAL", field_name, 0, {
                "status": "error",
                "message": f"{field_name} is required",
            }, None)
            return None
        return value

    def register_user(self):
        username = self._require_value(self.reg_username, "Username")
        password = self._require_value(self.reg_password, "Password")
        if username and password:
            self._dispatch_request("POST", "/register", {"username": username, "password": password})

    def login_user(self):
        username = self._require_value(self.login_username, "Username")
        password = self._require_value(self.login_password, "Password")
        if username and password:
            self._dispatch_request("POST", "/login", {"username": username, "password": password})

    def get_all_users(self):
        self._dispatch_request("GET", "/users", after_response=self._handle_get_all_users)

    def _handle_get_all_users(self, payload):
        users = payload.get("users", []) if payload.get("status") == "success" else []
        self._refresh_users_table(users)

    def get_one_user(self):
        username = self._require_value(self.lookup_username, "Username")
        if username:
            self._dispatch_request("GET", f"/users/{username}", after_response=self._handle_get_one_user)

    def _handle_get_one_user(self, payload):
        user = payload.get("user") if payload.get("status") == "success" else None
        self._refresh_users_table([] if not user else [user])

    def update_user(self):
        username = self._require_value(self.update_username, "Username")
        password = self._require_value(self.update_password, "New Password")
        if username and password:
            self._dispatch_request("PUT", f"/users/{username}", {"password": password})

    def delete_user(self):
        username = self._require_value(self.delete_username, "Username")
        if username:
            self._dispatch_request("DELETE", f"/users/{username}")

    def _refresh_users_table(self, users):
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        for user in users:
            self.users_table.insert("", "end", values=(user.get("username", ""),))


if __name__ == "__main__":
    app = TkinterApiClient()
    app.mainloop()