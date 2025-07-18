# 🔑 API Setup Guide for Restaurant Search

This guide will help you set up the free API keys needed for the restaurant search functionality in the Proactive Work-Life Assistant.

## 📋 Required APIs

The assistant uses three free APIs to find real restaurants with their details, menus, and locations:

1. **Google Places API** - For restaurant details, ratings, and contact information
2. **OpenTripMap API** - For location-based restaurant search
3. **Zomato API** - For restaurant menus, cuisines, and detailed information

## 🆓 Free API Setup

### 1. Google Places API

**Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Places API" from the API Library

**Step 2: Create API Key**
1. Go to "Credentials" in the left sidebar
2. Click "Create Credentials" → "API Key"
3. Copy the generated API key

**Step 3: Restrict API Key (Recommended)**
1. Click on the created API key
2. Under "Application restrictions", select "HTTP referrers"
3. Add your domain or use "localhost" for development
4. Under "API restrictions", select "Restrict key" and choose "Places API"

**Free Tier:** $200 credit per month (approximately 28,000 requests)

### 2. OpenTripMap API

**Step 1: Get API Key**
1. Go to [OpenTripMap](https://opentripmap.io/)
2. Click "Get API Key"
3. Fill in the registration form
4. Copy the generated API key

**Free Tier:** 1,000 requests per day

### 3. Zomato API

**Step 1: Get API Key**
1. Go to [Zomato Developers](https://developers.zomato.com/)
2. Click "Get API Key"
3. Fill in the registration form
4. Copy the generated API key

**Free Tier:** 1,000 requests per day

## ⚙️ Configuration

### Step 1: Copy Environment File
```bash
cp config/env.example config/.env
```

### Step 2: Update Environment Variables
Edit `config/.env` and add your API keys:

```env
# Restaurant API Keys
GOOGLE_PLACES_API_KEY=your_google_places_key_here
OPENTRIPMAP_API_KEY=your_opentripmap_key_here
ZOMATO_API_KEY=your_zomato_key_here

# Restaurant Service Configuration
RESTAURANT_SERVICE=api
```

### Step 3: Test Configuration
Run the application and try a restaurant search query:
```
"Find restaurants with Hyderabadi biryani in Hyderabad"
```

## 🔍 How It Works

### Restaurant Search Process

1. **Location Resolution**: Uses OpenStreetMap (Nominatim) to get coordinates for the location
2. **Multi-API Search**: Searches across all available APIs simultaneously
3. **Data Aggregation**: Combines results from different sources
4. **Duplicate Removal**: Removes duplicate restaurants based on name and address
5. **Filtering**: Applies user preferences (rating, price, cuisine)
6. **Menu Retrieval**: Gets menu information from Zomato when available
7. **Ranking**: Sorts results by rating and relevance

### Data Sources

| API | Data Provided |
|-----|---------------|
| **Google Places** | Restaurant names, addresses, ratings, phone numbers, opening hours |
| **OpenTripMap** | Location-based restaurant search, basic details |
| **Zomato** | Detailed restaurant info, menus, cuisines, cost estimates |

## 🚀 Example Queries

Once configured, you can use queries like:

- "Find restaurants with Hyderabadi biryani in Hyderabad"
- "Search for Italian restaurants in Bangalore"
- "Find high-rated restaurants near Gachibowli"
- "Look for restaurants with good ratings in Mumbai"
- "Find restaurants with Chinese cuisine in Delhi"

## 🔧 Troubleshooting

### Common Issues

1. **No restaurants found**
   - Check if API keys are correctly set
   - Verify location spelling
   - Try a different location or cuisine

2. **API rate limit exceeded**
   - Wait for the rate limit to reset
   - Consider upgrading to paid plans for higher limits

3. **Location not found**
   - Try using more specific location names
   - Use city names instead of areas

### Testing API Keys

You can test your API keys individually:

```python
# Test Google Places API
import requests
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": "17.3850,78.4867",  # Hyderabad coordinates
    "radius": 5000,
    "type": "restaurant",
    "key": "YOUR_GOOGLE_API_KEY"
}
response = requests.get(url, params=params)
print(response.json())
```

## 💡 Tips for Best Results

1. **Use specific locations**: "Hyderabad" works better than "India"
2. **Specify cuisine types**: "Hyderabadi biryani" is more specific than "food"
3. **Include rating preferences**: The system filters by minimum ratings
4. **Check multiple sources**: Different APIs may have different restaurant data

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for all API keys
- Restrict API keys to specific domains/IPs when possible
- Monitor API usage to avoid unexpected charges

## 📞 Support

If you encounter issues:

1. Check the API documentation for each service
2. Verify your API keys are active and have sufficient quota
3. Test individual APIs using their respective documentation
4. Check the application logs for detailed error messages

---

**Note:** All APIs mentioned offer free tiers suitable for development and personal use. For production applications, consider upgrading to paid plans for higher limits and better support. 