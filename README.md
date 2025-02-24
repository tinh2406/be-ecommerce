# 🚀 E-Commerce Platform with Django Rest Framework  

![License](https://img.shields.io/badge/license-MIT-blue.svg)  
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)  
![Django Rest Framework](https://img.shields.io/badge/DRF-API-red)  

## 📌 Overview  

This repository contains a high-performance **e-commerce platform** built with **Django Rest Framework** and a set of cutting-edge technologies to ensure scalability, speed, and intelligent recommendations.  

## ✨ Key Features  

✅ **Django Rest Framework (DRF)** – The backbone of our API, ensuring a clean and maintainable architecture.  
✅ **MySQL** – A robust relational database for handling transactional data efficiently.  
✅ **Elasticsearch (ES)** – Supercharged search capabilities to provide fast and relevant results.  
✅ **Caching** – Optimized response times using caching strategies.  
✅ **RabbitMQ** – Asynchronous task processing to offload heavy operations and enhance system performance.  
✅ **Advanced AI & Deep Learning Algorithms** – Personalized product recommendations based on user behavior and trends.  
✅ **AI Agent** – Your personal shopping assistant, providing smart suggestions and support.  

## 🚀 Why This Project Stands Out?  

This isn't just another e-commerce backend. It's built to **scale**, **perform**, and **deliver** a superior user experience. With AI-powered recommendations and an intelligent chatbot, we go beyond traditional e-commerce and bring a **next-gen shopping experience** to life.  

## 📂 Project Structure  


# base_django

Monitor Celery tasks with Flower
```bash
celery -A core flower
```

Run Celery worker
```bash
celery -A core worker
```

Run Celery beat for periodic tasks
```bash
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Generate migrations
```bash
python manage makemigrations
python manage migrate
```
