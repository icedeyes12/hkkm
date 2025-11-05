"""
External Services Integration
Provides connections to weather, news, and custom webhook services
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class ExternalService:
    """Base class for external services"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.last_request_time = None
        self.cache = {}
        self.cache_duration = 300  # 5 minutes default
    
    def is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cache_entry = self.cache[key]
        if 'timestamp' not in cache_entry:
            return False
        
        elapsed = (datetime.now() - cache_entry['timestamp']).total_seconds()
        return elapsed < self.cache_duration
    
    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self.is_cache_valid(key):
            return self.cache[key]['data']
        return None
    
    def set_cache(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }


class WeatherService(ExternalService):
    """Weather data service using OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.cache_duration = 600  # 10 minutes for weather
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city"""
        cache_key = f"weather_{city}"
        cached = self.get_cached(cache_key)
        
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/weather",
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "success": True,
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "wind_speed": data["wind"]["speed"]
                }
                self.set_cache(cache_key, result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"Weather API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching weather: {str(e)}"
            }
    
    def get_forecast(self, city: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        cache_key = f"forecast_{city}_{days}"
        cached = self.get_cached(cache_key)
        
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                
                for item in data["list"][:days * 8]:
                    forecasts.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"]
                    })
                
                result = {
                    "success": True,
                    "city": data["city"]["name"],
                    "forecasts": forecasts
                }
                self.set_cache(cache_key, result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"Forecast API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching forecast: {str(e)}"
            }


class NewsService(ExternalService):
    """News service using NewsAPI"""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.cache_duration = 1800  # 30 minutes for news
    
    def get_top_headlines(self, country: str = "us", category: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """Get top news headlines"""
        cache_key = f"headlines_{country}_{category}_{limit}"
        cached = self.get_cached(cache_key)
        
        if cached:
            return cached
        
        try:
            params = {
                "apiKey": self.api_key,
                "country": country,
                "pageSize": limit
            }
            
            if category:
                params["category"] = category
            
            response = requests.get(
                f"{self.BASE_URL}/top-headlines",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "source": article.get("source", {}).get("name"),
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt")
                    })
                
                result = {
                    "success": True,
                    "total_results": data.get("totalResults", 0),
                    "articles": articles
                }
                self.set_cache(cache_key, result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"News API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error fetching news: {str(e)}"
            }
    
    def search_news(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search for news articles"""
        cache_key = f"search_{query}_{limit}"
        cached = self.get_cached(cache_key)
        
        if cached:
            return cached
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/everything",
                params={
                    "apiKey": self.api_key,
                    "q": query,
                    "pageSize": limit,
                    "sortBy": "publishedAt"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "source": article.get("source", {}).get("name"),
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt")
                    })
                
                result = {
                    "success": True,
                    "total_results": data.get("totalResults", 0),
                    "articles": articles
                }
                self.set_cache(cache_key, result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"News API Error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching news: {str(e)}"
            }


class WebhookService(ExternalService):
    """Custom webhook service for external integrations"""
    
    def __init__(self):
        super().__init__()
        self.webhooks = {}
    
    def register_webhook(self, name: str, url: str, method: str = "POST", headers: Optional[Dict] = None):
        """Register a custom webhook"""
        self.webhooks[name] = {
            "url": url,
            "method": method.upper(),
            "headers": headers or {}
        }
    
    def call_webhook(self, name: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Call a registered webhook"""
        if name not in self.webhooks:
            return {
                "success": False,
                "error": f"Webhook '{name}' not found"
            }
        
        webhook = self.webhooks[name]
        
        try:
            if webhook["method"] == "GET":
                response = requests.get(
                    webhook["url"],
                    headers=webhook["headers"],
                    params=data,
                    timeout=10
                )
            else:  # POST
                response = requests.post(
                    webhook["url"],
                    headers=webhook["headers"],
                    json=data,
                    timeout=10
                )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook error: {str(e)}"
            }
    
    def list_webhooks(self) -> List[str]:
        """List all registered webhooks"""
        return list(self.webhooks.keys())


class ServiceManager:
    """Manager for all external services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weather = None
        self.news = None
        self.webhooks = WebhookService()
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize services based on configuration"""
        # Initialize weather service
        if "weather_api_key" in self.config and self.config["weather_api_key"]:
            self.weather = WeatherService(self.config["weather_api_key"])
        
        # Initialize news service
        if "news_api_key" in self.config and self.config["news_api_key"]:
            self.news = NewsService(self.config["news_api_key"])
        
        # Register custom webhooks
        if "webhooks" in self.config:
            for webhook in self.config["webhooks"]:
                self.webhooks.register_webhook(
                    webhook["name"],
                    webhook["url"],
                    webhook.get("method", "POST"),
                    webhook.get("headers")
                )
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a service is available"""
        if service_name == "weather":
            return self.weather is not None
        elif service_name == "news":
            return self.news is not None
        elif service_name == "webhooks":
            return len(self.webhooks.list_webhooks()) > 0
        return False
    
    def get_available_services(self) -> List[str]:
        """Get list of available services"""
        services = []
        if self.weather:
            services.append("weather")
        if self.news:
            services.append("news")
        if self.webhooks.list_webhooks():
            services.append("webhooks")
        return services
