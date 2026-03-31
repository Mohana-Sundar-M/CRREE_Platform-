from crree_env.models import Task

TASKS = [
    Task(
        id="task_1_easy",
        name="Missing Null Check",
        description="A simple bug where a null check is missing before accessing a field.",
        difficulty="easy",
        diff="""--- user_service.py
+++ user_service.py
@@ -10,5 +10,5 @@
     def get_user_email(self, user_id):
         user = self.db.find_user(user_id)
-        return user.email
+        return user.email if user else None
""",
        ground_truth_issues=["Potential NullPointerException when user is not found."],
        ground_truth_severity=["high"],
        expected_suggestions_keywords=[["null check", "if user", "None"]]
    ),
    Task(
        id="task_2_medium",
        name="Logic Flaw & Edge Case",
        description="A logic flaw in a discount calculator that doesn't handle negative amounts correctly.",
        difficulty="medium",
        diff="""--- calculator.py
+++ calculator.py
@@ -5,7 +5,10 @@
     def calculate_discount(self, price, discount_rate):
+        if price < 0:
+            raise ValueError("Price cannot be negative")
         if discount_rate > 1.0:
             return price * 0.5 # Default to 50% if rate is too high
-        return price * (1 - discount_rate)
+        return price * (1 - max(0, discount_rate))
""",
        ground_truth_issues=[
            "Missing validation for negative price.",
            "Discount rate could be negative, leading to price increase."
        ],
        ground_truth_severity=["medium", "medium"],
        expected_suggestions_keywords=[
            ["negative price", "ValueError", "validation"],
            ["max(0", "negative discount", "clamp"]
        ]
    ),
    Task(
        id="task_3_hard",
        name="Security & Performance",
        description="A task containing a SQL injection vulnerability and an inefficient loop.",
        difficulty="hard",
        diff="""--- data_manager.py
+++ data_manager.py
@@ -15,10 +15,12 @@
     def get_user_data(self, username):
-        query = f"SELECT * FROM users WHERE username = '{username}'"
-        return self.db.execute(query)
+        query = "SELECT * FROM users WHERE username = ?"
+        return self.db.execute(query, (username,))
 
     def process_items(self, items):
-        results = []
-        for item in items:
-            if item in self.cache:
-                results.append(self.cache[item])
-        return results
+        return [self.cache[item] for item in items if item in self.cache]
""",
        ground_truth_issues=[
            "SQL Injection vulnerability due to string formatting in query.",
            "Inefficient list extension in loop (can be optimized with list comprehension or bulk lookup)."
        ],
        ground_truth_severity=["critical", "medium"],
        expected_suggestions_keywords=[
            ["SQL Injection", "parameterized", "prepared statement"],
            ["list comprehension", "efficiency", "optimization"]
        ]
    ),
    Task(
        id="task_4_security",
        name="Weak Crypto & Hardcoded Creds",
        description="A task containing weak encryption (MD5) and a hardcoded API key.",
        difficulty="hard",
        diff="""--- auth_provider.py
+++ auth_provider.py
@@ -1,10 +1,12 @@
 import hashlib
+import os
 
-API_KEY = "sk_live_1234567890abcdef"
+API_KEY = os.getenv("AUTH_API_KEY")
 
 def hash_password(password):
-    return hashlib.md5(password.encode()).hexdigest()
+    # MD5 is broken, use Argon2 or bcrypt
+    import bcrypt
+    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
""",
        ground_truth_issues=[
            "Hardcoded API key in source code.",
            "Use of insecure MD5 hashing for passwords."
        ],
        ground_truth_severity=["critical", "critical"],
        expected_suggestions_keywords=[
            ["environment variable", "os.getenv", "hardcoded"],
            ["bcrypt", "Argon2", "security", "insecure"]
        ]
    ),
    Task(
        id="task_5_performance",
        name="N+1 Query Problem",
        description="A list view that fetches related items in a loop, causing excessive DB calls.",
        difficulty="hard",
        diff="""--- store_manager.py
+++ store_manager.py
@@ -10,12 +10,18 @@
     def get_store_details(self, store_ids):
         results = []
-        for sid in store_ids:
-            store = self.db.query(f"SELECT * FROM stores WHERE id={sid}")
-            results.append(store)
+        # Optimization: use IN clause for bulk fetch
+        stores = self.db.query("SELECT * FROM stores WHERE id IN ?", (tuple(store_ids),))
+        return stores
""",
        ground_truth_issues=[
            "N+1 query problem: fetching stores in a loop.",
            "Potential for SQL injection via sid interpolation."
        ],
        ground_truth_severity=["high", "medium"],
        expected_suggestions_keywords=[
            ["N+1", "loop", "bulk fetch", "tuple"],
            ["SQL injection", "parameterized"]
        ]
    ),
    Task(
        id="task_6_architecture",
        name="Tight Coupling",
        description="A class that directly instantiates its dependencies, making it hard to test.",
        difficulty="medium",
        diff="""--- payment_processor.py
+++ payment_processor.py
@@ -5,11 +5,14 @@
 class PaymentProcessor:
-    def __init__(self):
-        self.gateway = StripeGateway()
+    def __init__(self, gateway=None):
+        self.gateway = gateway or StripeGateway()
""",
        ground_truth_issues=[
            "Tight coupling to StripeGateway prevents easy mocking/testing.",
            "Missing dependency injection."
        ],
        ground_truth_severity=["medium", "medium"],
        expected_suggestions_keywords=[
            ["dependency injection", "mocking", "testing"],
            ["tight coupling", "StripeGateway"]
        ]
    )
 ]
 
def get_task_by_id(task_id: str) -> Task:
    for task in TASKS:
        if task.id == task_id:
            return task
    raise ValueError(f"Task {task_id} not found")
