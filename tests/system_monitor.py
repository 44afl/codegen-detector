#!/usr/bin/env python
"""
System Monitor during Load Tests
Tracks CPU, Memory, and other metrics while tests run
"""

import psutil
import threading
import time
import csv
import os
from datetime import datetime
from pathlib import Path

class SystemMonitor:
    """Monitors system resources during load testing"""
    
    def __init__(self, output_file=None):
        if output_file is None:
            # Use absolute path based on script location
            script_dir = Path(__file__).parent
            output_file = script_dir / "system_metrics.csv"
        self.output_file = output_file
        self.running = False
        self.thread = None
        self.start_time = None
        self.metrics = []
        
        # Create output directory if needed
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start monitoring in background thread"""
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print(f"✓ System monitoring started. Logging to {self.output_file}")
    
    def stop(self):
        """Stop monitoring and save results"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self._save_results()
        print(f"✓ System monitoring stopped. Results saved to {self.output_file}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                elapsed = time.time() - self.start_time
                
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count()
                
                # Memory metrics
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_mb = memory.used / (1024 ** 2)
                
                # Process metrics (if Flask is running)
                flask_process = None
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'python' in proc.name().lower():
                        try:
                            if 'flask' in ' '.join(proc.cmdline()).lower() or \
                               'main.py' in ' '.join(proc.cmdline()).lower():
                                flask_process = proc
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                
                process_cpu = 0
                process_memory = 0
                if flask_process:
                    try:
                        process_cpu = flask_process.cpu_percent()
                        process_memory = flask_process.memory_info().rss / (1024 ** 2)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                
                metric = {
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_sec': round(elapsed, 2),
                    'cpu_percent': round(cpu_percent, 2),
                    'cpu_count': cpu_count,
                    'memory_percent': round(memory_percent, 2),
                    'memory_mb': round(memory_mb, 2),
                    'flask_cpu_percent': round(process_cpu, 2),
                    'flask_memory_mb': round(process_memory, 2),
                    'disk_read_mb': round(disk_io.read_bytes / (1024 ** 2), 2),
                    'disk_write_mb': round(disk_io.write_bytes / (1024 ** 2), 2),
                }
                
                self.metrics.append(metric)
                
                # Print every 10 seconds
                if int(elapsed) % 10 == 0 and elapsed > 0:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                          f"CPU: {cpu_percent}% | Memory: {memory_percent}% ({memory_mb:.0f}MB) | "
                          f"Flask CPU: {process_cpu}% | Flask Mem: {process_memory:.0f}MB")
                
                time.sleep(2)  # Sample every 2 seconds
                
            except Exception as e:
                print(f"Error in monitoring: {e}")
    
    def _save_results(self):
        """Save metrics to CSV"""
        if not self.metrics:
            print("No metrics to save.")
            return
        
        try:
            # Ensure parent directory exists
            Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
            
            keys = self.metrics[0].keys()
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.metrics)
            print(f"✓ CSV saved successfully: {self.output_file}")
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.metrics:
            return
        
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        mem_values = [m['memory_percent'] for m in self.metrics]
        flask_cpu_values = [m['flask_cpu_percent'] for m in self.metrics if m['flask_cpu_percent'] > 0]
        flask_mem_values = [m['flask_memory_mb'] for m in self.metrics if m['flask_memory_mb'] > 0]
        
        print("\n" + "="*70)
        print("SYSTEM RESOURCE SUMMARY")
        print("="*70)
        
        if cpu_values:
            print(f"\nCPU Usage:")
            print(f"  Min:  {min(cpu_values):.2f}%")
            print(f"  Avg:  {sum(cpu_values)/len(cpu_values):.2f}%")
            print(f"  Max:  {max(cpu_values):.2f}%")
        
        if mem_values:
            print(f"\nSystem Memory:")
            print(f"  Min:  {min(mem_values):.2f}%")
            print(f"  Avg:  {sum(mem_values)/len(mem_values):.2f}%")
            print(f"  Max:  {max(mem_values):.2f}%")
        
        if flask_cpu_values:
            print(f"\nFlask Process CPU:")
            print(f"  Min:  {min(flask_cpu_values):.2f}%")
            print(f"  Avg:  {sum(flask_cpu_values)/len(flask_cpu_values):.2f}%")
            print(f"  Max:  {max(flask_cpu_values):.2f}%")
        
        if flask_mem_values:
            print(f"\nFlask Process Memory:")
            print(f"  Min:  {min(flask_mem_values):.2f} MB")
            print(f"  Avg:  {sum(flask_mem_values)/len(flask_mem_values):.2f} MB")
            print(f"  Max:  {max(flask_mem_values):.2f} MB")
        
        print("\n" + "="*70 + "\n")

# Global monitor instance
_monitor = None

def get_monitor():
    """Get or create monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor

if __name__ == "__main__":
    # Standalone usage: python tests/system_monitor.py
    monitor = SystemMonitor()
    monitor.start()
    
    try:
        print("Monitoring system resources. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        monitor.print_summary()
