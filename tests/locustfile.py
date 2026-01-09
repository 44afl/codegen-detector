"""
Load and Stress Testing Suite for CodeGen Detector
Using Locust framework for scalable testing
"""

from locust import HttpUser, task, between, TaskSet, events
import random
import json
import time
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================
BASE_URL = "http://localhost:5000"  # Change to your Flask backend URL
SAMPLE_CODE_SNIPPETS = [
    "def hello_world():\n    print('Hello, World!')\n    return 42",
    "function factorial(n) {\n    if (n <= 1) return 1;\n    return n * factorial(n-1);\n}",
    "public class Solution {\n    public int sum(int[] nums) {\n        int result = 0;\n        for (int num : nums) result += num;\n        return result;\n    }\n}",
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "const reverseString = (str) => str.split('').reverse().join('');",
]

# ============================================================================
# Performance Event Handlers
# ============================================================================
class PerfStats:
    """Tracks detailed performance metrics"""
    def __init__(self):
        self.request_times = []
        self.errors = 0
        self.total_requests = 0
    
    def record(self, response_time, is_error=False):
        self.request_times.append(response_time)
        self.total_requests += 1
        if is_error:
            self.errors += 1
    
    def get_stats(self):
        if not self.request_times:
            return {}
        sorted_times = sorted(self.request_times)
        return {
            'min': min(sorted_times),
            'max': max(sorted_times),
            'avg': sum(sorted_times) / len(sorted_times),
            'p50': sorted_times[len(sorted_times) // 2],
            'p95': sorted_times[int(len(sorted_times) * 0.95)],
            'p99': sorted_times[int(len(sorted_times) * 0.99)],
            'error_rate': (self.errors / self.total_requests * 100) if self.total_requests > 0 else 0
        }

perf_stats = PerfStats()

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Listener for every request - tracks performance"""
    perf_stats.record(response_time, exception is not None)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Generate final statistics when test ends"""
    stats = perf_stats.get_stats()
    print("\n" + "="*70)
    print("LOAD TEST RESULTS - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    print(f"Total Requests: {perf_stats.total_requests}")
    print(f"Total Errors: {perf_stats.errors}")
    print(f"Error Rate: {stats.get('error_rate', 0):.2f}%")
    print("\nResponse Times (ms):")
    print(f"  Min:  {stats.get('min', 0):.2f}")
    print(f"  Avg:  {stats.get('avg', 0):.2f}")
    print(f"  P50:  {stats.get('p50', 0):.2f}")
    print(f"  P95:  {stats.get('p95', 0):.2f}")
    print(f"  P99:  {stats.get('p99', 0):.2f}")
    print(f"  Max:  {stats.get('max', 0):.2f}")
    print("="*70 + "\n")

# ============================================================================
# Test Scenarios
# ============================================================================

class PredictionTasks(TaskSet):
    """Core prediction endpoint tests"""
    
    @task(4)
    def predict_adaboost(self):
        """Test AdaBoost prediction"""
        code = random.choice(SAMPLE_CODE_SNIPPETS)
        # API expects file upload, not JSON
        files = {
            "file": ("test.py", code.encode('utf-8'), "text/plain")
        }
        with self.client.post(
            "/predict/adaboost",
            files=files,
            catch_response=True,
            timeout=30
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def predict_svm(self):
        """Test SVM prediction"""
        code = random.choice(SAMPLE_CODE_SNIPPETS)
        files = {
            "file": ("test.py", code.encode('utf-8'), "text/plain")
        }
        with self.client.post(
            "/predict/svm",
            files=files,
            catch_response=True,
            timeout=30
        ) as response:
            if response.status_code in [200, 503]:  # 503 if model not loaded
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def predict_lstm(self):
        """Test LSTM prediction"""
        code = random.choice(SAMPLE_CODE_SNIPPETS)
        files = {
            "file": ("test.py", code.encode('utf-8'), "text/plain")
        }
        with self.client.post(
            "/predict/lstm",
            files=files,
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code in [200, 503]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def predict_transformer(self):
        """Test Transformer prediction"""
        code = random.choice(SAMPLE_CODE_SNIPPETS)
        files = {
            "file": ("test.py", code.encode('utf-8'), "text/plain")
        }
        with self.client.post(
            "/predict/transformer",
            files=files,
            catch_response=True,
            timeout=60
        ) as response:
            if response.status_code in [200, 503]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

class AuthenticationTasks(TaskSet):
    """Authentication and user management tests"""
    
    @task(2)
    def login(self):
        """Test login endpoint"""
        payload = {
            "email": f"test{random.randint(1, 1000)}@example.com",
            "password": "testpass123"
        }
        with self.client.post(
            "/auth/login",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def signup(self):
        """Test signup endpoint"""
        payload = {
            "email": f"loadtest{random.randint(10000, 99999)}@example.com",
            "password": "testpass123",
            "full_name": "Load Test User"
        }
        with self.client.post(
            "/auth/signup",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code in [200, 400, 409]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

class HealthCheckTasks(TaskSet):
    """Health and diagnostic endpoint tests"""
    
    @task(1)
    def subscription_plans(self):
        """Test subscription plans endpoint"""
        with self.client.get(
            "/subscriptions/plans",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def legal_terms(self):
        """Test legal terms endpoint"""
        with self.client.get(
            "/legal/terms",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

# ============================================================================
# Load Test User Classes
# ============================================================================

class RegularUser(HttpUser):
    """Simulates regular user behavior - mostly predictions"""
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    tasks = {
        PredictionTasks: 70,
        AuthenticationTasks: 20,
        HealthCheckTasks: 10
    }

class HeavyUser(HttpUser):
    """Simulates power user - rapid requests"""
    wait_time = between(0.5, 1.5)  # More frequent requests
    tasks = {
        PredictionTasks: 80,
        AuthenticationTasks: 15,
        HealthCheckTasks: 5
    }

class StressTestUser(HttpUser):
    """Simulates stress conditions - minimal wait time"""
    wait_time = between(0.1, 0.5)  # Very rapid requests
    tasks = {
        PredictionTasks: 85,
        AuthenticationTasks: 10,
        HealthCheckTasks: 5
    }
