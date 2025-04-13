# 2025 NTUIM LSAP Mini-Project - **IM in Love**

## Overview

As an Infrastructure Engineer at IM.Inc—a startup building a campus-focused dating app—your primary objective is to migrate the existing backend system to Google Cloud Platform (GCP), leveraging the Google Kubernetes Engine (GKE) service.

The current backend consists of several components, including user data storage, user interaction processing, image storage, and image compression. Depending on their function, these services may be CPU-bound, memory-bound, disk-bound, or I/O-bound.

GCP offers $300 in free credits for new accounts, which you can take advantage of during the migration process. Learn more about GCP free credits[https://cloud.google.com/free/docs/free-cloud-features].

Your project will be assessed based on the following performance metrics:

(a) **Throughput** – The number of requests the system can handle within a given time frame

(b) **Latency** – Measured at the 95th percentile to evaluate response time consistency

(c) **Success Rate** – The percentage of requests that return the correct data

(d) **Cost Efficiency** – The total cost incurred on GCP for running the backend infrastructure


## Scenarios

The backend system will be evaluated under the following five scenarios to assess its robustness, scalability, and responsiveness across varying workloads and stress conditions:

### (a) Light Load – 10 pts  
A small number of users interact with the system concurrently, simulating off-peak or idle periods. This scenario measures baseline performance, resource utilization efficiency, and overall system responsiveness when demand is low.

### (b) Regular Load – 15 pts  
Represents standard day-to-day usage with a typical number of concurrent users. This tests the system’s ability to maintain stable throughput, low latency, and high availability under expected operating conditions.

### (c) Heavy Load – 20 pts  
Simulates peak usage with a large volume of concurrent users and requests. This scenario evaluates the backend’s scalability, auto-scaling responsiveness, fault tolerance, and ability to sustain performance under high stress.

### (d) Special Case 1: Rapid Messaging – 15 pts (Evaluation script not provided)
A sudden spike in real-time, high-frequency messaging activity (e.g., during campus-wide events or app launches). This tests the system’s ability to handle bursty I/O-bound workloads while maintaining low latency, message integrity, and throughput.

### (e) Special Case 2: DDoS Simulation – 15 pts (Evaluation script not provided)
An intentional flood of malicious or unauthenticated traffic simulates a Distributed Denial-of-Service (DDoS) attack. This assesses the system’s defense mechanisms—such as rate-limiting, request validation, IP throttling, and traffic filtering—to ensure continued availability and protect core services under threat.

You will also be evaluated on the following components:

### (f) Spending – 15 pts  
Evaluate how cost-effectively your solution utilizes Google Cloud resources. Minimize unnecessary expenses while maintaining performance. Points will be awarded based on budget-conscious design choices, use of autoscaling, and efficient resource provisioning.

### (g) Report – 10 pts  
Submit a clear and comprehensive technical report detailing your system design, deployment architecture, testing methodology, observed performance metrics, and justifications for key decisions. The report should demonstrate both technical depth and clarity in communication.